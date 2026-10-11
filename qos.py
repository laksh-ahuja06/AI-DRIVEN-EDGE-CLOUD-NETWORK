"""
QoS scheduler for the edge gateway's constrained backbone link
(spec 9.4, 11.3 steps 22-23, FIG. 7).

The scheduler is pure logic with an injected clock, so the *same* code is
used by the live gateway (edge_gateway.py) and by the discrete-event
evaluation (evaluate.py).

Model of the backbone: a token bucket of `rate_bps` bytes/second (e.g. a
9.6-16 kbps satellite/microwave backhaul). Each packet costs its JSON size
plus 28 bytes of UDP/IP header.

Policies
  fifo      one queue, first come first served - the "treat every byte
            equally" baseline the spec argues against.
  priority  three queues served in strict priority
            CRITICAL > NORMAL > NON_ESSENTIAL, and while a cyclone alert
            is active:
              * bandwidth reservation: NORMAL / NON_ESSENTIAL packets may
                only be sent if `reserve_bytes` of link credit stays free
                afterwards, so a CRITICAL packet arriving next is sent
                immediately instead of waiting behind them;
              * NON_ESSENTIAL traffic is shed at the gateway when the link
                is congested (more than `shed_backlog_s` seconds of traffic
                already queued). With spare capacity it is still delivered,
                so the scheduler never wastes an idle link.
"""
from collections import deque

from common import TRAFFIC_CLASSES, TRAFFIC_CRITICAL, TRAFFIC_NON_ESSENTIAL, TRAFFIC_NORMAL

UDP_IP_OVERHEAD = 28


class TokenBucket:
    def __init__(self, rate, burst, now=0.0):
        self.rate = float(rate)
        self.burst = float(burst)
        self.tokens = float(burst)
        self.last = now

    def refill(self, now):
        if now > self.last:
            self.tokens = min(self.burst, self.tokens + (now - self.last) * self.rate)
            self.last = now

    def time_until(self, size, now):
        self.refill(now)
        return 0.0 if self.tokens >= size else (size - self.tokens) / self.rate


class ClassStats:
    __slots__ = ("enqueued", "sent", "dropped", "shed", "wait_sum", "wait_max", "recent_waits", "bytes")

    def __init__(self):
        self.enqueued = self.sent = self.dropped = self.shed = self.bytes = 0
        self.wait_sum = self.wait_max = 0.0
        self.recent_waits = deque(maxlen=500)

    def as_dict(self):
        waits = sorted(self.recent_waits)
        p95 = waits[int(0.95 * (len(waits) - 1))] if waits else 0.0
        return {
            "enqueued": self.enqueued,
            "sent": self.sent,
            "dropped": self.dropped,
            "shed": self.shed,
            "bytes": self.bytes,
            "avg_wait_ms": round(1000 * self.wait_sum / self.sent, 1) if self.sent else 0.0,
            "p95_wait_ms": round(1000 * p95, 1),
            "max_wait_ms": round(1000 * self.wait_max, 1),
        }


class QoSScheduler:
    def __init__(self, rate_bps=1500, burst_bytes=None, policy="priority", max_queue=200,
                 reserve_bytes=700, shed_backlog_s=1.0, now=0.0):
        if policy not in ("fifo", "priority"):
            raise ValueError("policy must be 'fifo' or 'priority'")
        self.policy = policy
        self.rate_bps = rate_bps
        # Burst must exceed the largest packet plus the critical reserve.
        burst = burst_bytes or max(2048 + reserve_bytes, rate_bps // 2)
        self.link = TokenBucket(rate_bps, burst, now)
        self.reserve_bytes = reserve_bytes
        self.shed_backlog_bytes = shed_backlog_s * rate_bps
        self.queued_bytes = 0
        self.max_queue = max_queue
        self.alert = False
        self.queues = {c: deque() for c in TRAFFIC_CLASSES}
        self.fifo = deque()
        self.stats = {c: ClassStats() for c in TRAFFIC_CLASSES}

    @staticmethod
    def packet_size(payload_len):
        return payload_len + UDP_IP_OVERHEAD

    def set_alert(self, alert):
        self.alert = bool(alert)

    def queue_len(self, cls=None):
        if self.policy == "fifo":
            return len(self.fifo) if cls is None else sum(1 for _, c, _, _ in self.fifo if c == cls)
        if cls is None:
            return sum(len(q) for q in self.queues.values())
        return len(self.queues[cls])

    def enqueue(self, item, cls, size, now):
        """Returns True if accepted, False if dropped (queue full) or shed (alert)."""
        st = self.stats[cls]
        if (self.policy == "priority" and self.alert and cls == TRAFFIC_NON_ESSENTIAL
                and self.queued_bytes > self.shed_backlog_bytes):
            st.shed += 1
            return False
        if self.policy == "fifo":
            if len(self.fifo) >= self.max_queue:
                st.dropped += 1
                return False
            self.fifo.append((now, cls, size, item))
        else:
            q = self.queues[cls]
            if len(q) >= self.max_queue:
                st.dropped += 1
                return False
            q.append((now, cls, size, item))
        self.queued_bytes += size
        st.enqueued += 1
        return True

    def _candidates(self):
        if self.policy == "fifo":
            return [self.fifo]
        return [self.queues[c] for c in (TRAFFIC_CRITICAL, TRAFFIC_NORMAL, TRAFFIC_NON_ESSENTIAL)]

    def _head(self):
        """(queue, needed link credit) for the packet that must go next, or (None, None)."""
        for q in self._candidates():
            if q:
                _, cls, size, _ = q[0]
                reserve = self.reserve_bytes if (self.policy == "priority" and self.alert
                                                 and cls != TRAFFIC_CRITICAL) else 0
                return q, size + reserve
        return None, None

    def dequeue(self, now):
        """
        Returns (item, cls, wait_seconds) if a packet may be transmitted now,
        otherwise None. Call next_ready_in() to know how long to sleep.
        """
        self.link.refill(now)
        q, need = self._head()
        if q is None or self.link.tokens < need:
            return None
        t_in, cls, size, item = q.popleft()
        self.link.tokens -= size
        self.queued_bytes -= size
        st = self.stats[cls]
        wait = now - t_in
        st.sent += 1
        st.bytes += size
        st.wait_sum += wait
        st.wait_max = max(st.wait_max, wait)
        st.recent_waits.append(wait)
        return item, cls, wait

    def next_ready_in(self, now):
        """Seconds until dequeue() could succeed (None if every queue is empty)."""
        q, need = self._head()
        return None if q is None else self.link.time_until(need, now)

    def snapshot(self):
        return {
            "policy": self.policy,
            "alert": self.alert,
            "rate_bps": self.rate_bps,
            "queued": {c: self.queue_len(c) for c in TRAFFIC_CLASSES},
            "classes": {c: s.as_dict() for c, s in self.stats.items()},
        }
