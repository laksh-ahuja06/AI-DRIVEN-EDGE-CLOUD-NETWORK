"""
Edge Gateway
-------------
Receives raw telemetry (UDP) from buoys, radars, satellite ground
stations and ESP32 hardware nodes, then:

  1. parse / validate      - malformed packets are counted and dropped
  2. edge AI classification - CRITICAL / NORMAL / NON_ESSENTIAL using the
                              rule baseline, the trained ML classifier, or
                              both ("hybrid", default)
  3. AI-driven QoS          - forwards to the central server through a
                              token-bucket-limited backbone with strict
                              priority, alert-time shedding and bandwidth
                              reservation (see qos.py)
  4. feedback               - the server's fused risk (QoS feedback, FIG. 8)
                              can also put the gateway into alert mode, and
                              the gateway notifies hardware nodes so their
                              alert LED/buzzer switches on.

Spec sections 9.3, 9.4, 10, 11.3; FIG. 5, 7, 8.

Usage:
    python edge_gateway.py                         # hybrid policy, 1.5 KB/s backbone
    python edge_gateway.py --policy rule
    python edge_gateway.py --scheduler fifo        # baseline without QoS
    python edge_gateway.py --backbone-bps 1000     # tighter link
"""
import argparse
import json
import socket
import threading
import time

from common import (
    BIND_HOST,
    GATEWAY_CONTROL_PORT,
    GATEWAY_TO_SERVER_PORT,
    KIND_EDGE_FEATURE,
    KIND_GATEWAY_STATS,
    KIND_SENSOR,
    NODE_ALERT_PORT,
    SENSOR_TO_GATEWAY_PORT,
    SERVER_HOST,
    TRAFFIC_CRITICAL,
    TRAFFIC_NORMAL,
    ValidationError,
    classify_traffic,
    decode,
    encode,
    validate,
)
from edge_ai import QOS_MODEL_PATH, NodeHistory, QoSClassifier, trend_features
from qos import QoSScheduler

ALERT_HOLD_SECONDS = 10.0


class Gateway:
    def __init__(self, policy="hybrid", scheduler="priority", backbone_bps=1500, server_host=SERVER_HOST,
                 server_port=GATEWAY_TO_SERVER_PORT, clock=time.monotonic, verbose=True):
        self.clock = clock
        self.verbose = verbose
        self.server_addr = (server_host, server_port)
        self.sched = QoSScheduler(rate_bps=backbone_bps, policy=scheduler, now=clock())
        self.cond = threading.Condition()
        self.history = NodeHistory()
        self.node_addrs = {}            # node id -> (ip, port) for alert notifications
        self.last_local_critical = -1e9
        self.server_alert = False
        self.server_risk = 0.0
        self.alert = False
        self.invalid = 0
        self.ml_early = 0               # packets the ML flagged CRITICAL before the rule did
        self.policy = policy
        self.clf = None
        if policy in ("ml", "hybrid"):
            try:
                self.clf = QoSClassifier.load(QOS_MODEL_PATH)
            except FileNotFoundError:
                print(f"[gateway] {QOS_MODEL_PATH} not found - using the rule-based policy "
                      f"(run `python train_models.py`)")
                self.policy = "rule"
        self.out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def log(self, msg):
        if self.verbose:
            print(msg, flush=True)

    # ------------------------------------------------------------ classify
    def classify(self, record):
        rule_class = classify_traffic(record)
        if record.get("kind") != KIND_SENSOR or self.clf is None:
            return rule_class, None
        window = self.history.update(record)
        prob = float(self.clf.predict_proba(trend_features(window))[0])
        ml_critical = prob >= self.clf.threshold
        if self.policy == "ml":
            cls = TRAFFIC_CRITICAL if ml_critical else TRAFFIC_NORMAL
        else:  # hybrid: the rule is a safety floor, the ML adds early warning
            cls = TRAFFIC_CRITICAL if (ml_critical or rule_class == TRAFFIC_CRITICAL) else TRAFFIC_NORMAL
        if ml_critical and rule_class != TRAFFIC_CRITICAL:
            self.ml_early += 1
        return cls, round(prob, 3)

    # ------------------------------------------------------------ alerting
    def _update_alert(self, now):
        local = now - self.last_local_critical < ALERT_HOLD_SECONDS
        alert = local or self.server_alert
        if alert != self.alert:
            self.alert = alert
            self.sched.set_alert(alert)
            reason = "local critical traffic" if local else ("server risk feedback" if alert else "")
            self.log(f"[gateway] cyclone alert {'ACTIVE (' + reason + ')' if alert else 'cleared'} -> "
                     f"{'critical bandwidth reserved, non-essential shed' if alert else 'standard QoS restored'}")
            self._notify_nodes()

    def _notify_nodes(self):
        msg = encode({"type": "alert", "alert": self.alert, "risk": self.server_risk})
        for node, (ip, _port) in list(self.node_addrs.items()):
            try:
                self.out.sendto(msg, (ip, NODE_ALERT_PORT))
            except OSError:
                pass

    # ------------------------------------------------------------ ingest
    def handle_packet(self, data, addr=None):
        """Parse, validate, classify and enqueue one datagram. Returns the record or None."""
        now = self.clock()
        try:
            record = validate(decode(data))
        except (ValidationError, ValueError, UnicodeDecodeError) as exc:
            self.invalid += 1
            self.log(f"[gateway] dropped invalid packet from {addr}: {exc}")
            return None

        cls, prob = self.classify(record)
        record["traffic_class"] = cls
        record["qos_policy"] = self.policy
        if prob is not None:
            record["ml_prob"] = prob
        record["t_gw"] = round(time.time(), 3)
        if addr and record.get("kind") in (KIND_SENSOR, KIND_EDGE_FEATURE):
            self.node_addrs[record["node"]] = addr

        payload = encode(record)
        with self.cond:
            if cls == TRAFFIC_CRITICAL:
                self.last_local_critical = now
            self._update_alert(now)
            accepted = self.sched.enqueue(payload, cls, self.sched.packet_size(len(payload)), now)
            self.cond.notify()
        if not accepted:
            self.log(f"[gateway] {cls:13s} {record['node']} seq={record['seq']} "
                     f"{'shed (alert active)' if self.alert else 'dropped (queue full)'}")
        return record

    # ------------------------------------------------------------ threads
    def receiver(self, bind_host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((bind_host, port))
        self.log(f"[gateway] listening for sensors on {bind_host}:{port} "
                 f"(policy={self.policy}, scheduler={self.sched.policy}, backbone={self.sched.rate_bps} B/s)")
        while True:
            data, addr = sock.recvfrom(65535)
            self.handle_packet(data, addr)

    def forwarder(self):
        while True:
            with self.cond:
                now = self.clock()
                self._update_alert(now)
                item = self.sched.dequeue(now)
                if item is None:
                    wait = self.sched.next_ready_in(now)
                    self.cond.wait(timeout=0.5 if wait is None else min(0.5, max(0.001, wait)))
                    continue
            payload, cls, wait = item
            self.out.sendto(payload, self.server_addr)
            if self.verbose:
                rec = json.loads(payload)
                note = "  (alert: critical reserve held)" if self.alert and cls != TRAFFIC_CRITICAL else ""
                self.log(f"[gateway] {cls:13s} {rec['node']} seq={rec['seq']} forwarded "
                         f"after {wait * 1000:.0f} ms{note}")

    def control_listener(self, bind_host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((bind_host, port))
        while True:
            data, _ = sock.recvfrom(4096)
            try:
                msg = decode(data)
            except ValueError:
                continue
            if msg.get("type") == "qos_feedback":
                with self.cond:
                    self.server_alert = bool(msg.get("alert"))
                    self.server_risk = float(msg.get("risk", 0.0))
                    self._update_alert(self.clock())

    def stats_reporter(self, interval=2.0):
        seq = 0
        while True:
            time.sleep(interval)
            seq += 1
            with self.cond:
                snap = self.sched.snapshot()
                self._notify_nodes()  # periodic resync so rebooted hardware nodes learn the alert state
            snap.update({"node": "GATEWAY", "seq": seq, "kind": KIND_GATEWAY_STATS, "classifier": self.policy,
                         "invalid": self.invalid, "ml_early": self.ml_early, "server_risk": self.server_risk,
                         "t_sent": round(time.time(), 3)})
            self.out.sendto(encode(snap), self.server_addr)

    def run(self, bind_host=BIND_HOST, sensor_port=SENSOR_TO_GATEWAY_PORT, control_port=GATEWAY_CONTROL_PORT):
        threading.Thread(target=self.receiver, args=(bind_host, sensor_port), daemon=True).start()
        threading.Thread(target=self.control_listener, args=(bind_host, control_port), daemon=True).start()
        threading.Thread(target=self.stats_reporter, daemon=True).start()
        self.forwarder()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Edge gateway: edge AI classification + AI-driven QoS")
    parser.add_argument("--policy", choices=["rule", "ml", "hybrid"], default="hybrid",
                        help="Traffic classifier (default: hybrid = rule OR ML early warning)")
    parser.add_argument("--scheduler", choices=["priority", "fifo"], default="priority",
                        help="Backbone scheduler (fifo = no-QoS baseline)")
    parser.add_argument("--backbone-bps", type=int, default=1500, help="Backbone capacity in bytes/second")
    parser.add_argument("--server-host", default=SERVER_HOST)
    parser.add_argument("--server-port", type=int, default=GATEWAY_TO_SERVER_PORT)
    parser.add_argument("--bind", default=BIND_HOST)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    gw = Gateway(policy=args.policy, scheduler=args.scheduler, backbone_bps=args.backbone_bps,
                 server_host=args.server_host, server_port=args.server_port, verbose=not args.quiet)
    try:
        gw.run(bind_host=args.bind)
    except KeyboardInterrupt:
        print("[gateway] stopped")
