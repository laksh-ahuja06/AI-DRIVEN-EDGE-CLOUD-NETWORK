"""
Edge Gateway
-------------
Receives raw telemetry (UDP) from sensor nodes, performs lightweight
"edge AI" classification, and applies AI-driven QoS: CRITICAL traffic
(cyclone-threshold breaches) is forwarded first through a priority
queue, while NORMAL traffic is throttled whenever the network is in
an active cyclone alert (spec sections 9.3, 9.4, 10).

Usage:
    python edge_gateway.py
"""
import queue
import socket
import threading
import time

from common import (
    HOST,
    SENSOR_TO_GATEWAY_PORT,
    GATEWAY_TO_SERVER_PORT,
    classify_traffic,
    encode,
    decode,
    TRAFFIC_CRITICAL,
)

# Priority queue entries: (priority, insertion_order, record)
# priority 0 = CRITICAL (served first), priority 1 = NORMAL
pq = queue.PriorityQueue()
_counter = 0
_counter_lock = threading.Lock()

# Shared network state: flips on when recent traffic looks critical,
# which is the "dynamic QoS" trigger (reserve bandwidth for critical
# telemetry, throttle non-essential traffic).
cyclone_alert = threading.Event()
last_critical_time = [0.0]
ALERT_HOLD_SECONDS = 10.0


def receiver():
    """Listens for sensor telemetry, classifies it, and queues it."""
    global _counter
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, SENSOR_TO_GATEWAY_PORT))
    print(f"[gateway] listening for sensors on {HOST}:{SENSOR_TO_GATEWAY_PORT}")

    while True:
        data, _addr = sock.recvfrom(4096)
        record = decode(data)

        # ---- Edge AI step: classify traffic instead of treating every
        # byte equally (bandwidth-aware, cyclone-aware prioritization).
        traffic_class = classify_traffic(record)
        record["traffic_class"] = traffic_class

        if traffic_class == TRAFFIC_CRITICAL:
            last_critical_time[0] = time.time()
            cyclone_alert.set()
            priority = 0
        else:
            priority = 1

        with _counter_lock:
            _counter += 1
            order = _counter
        pq.put((priority, order, record))


def qos_forwarder():
    """
    AI-driven QoS module: drains the priority queue and forwards
    packets to the central prediction server. CRITICAL traffic is sent
    immediately; NORMAL traffic is throttled while a cyclone alert is
    active, freeing bandwidth for the data that matters.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        if cyclone_alert.is_set() and time.time() - last_critical_time[0] > ALERT_HOLD_SECONDS:
            cyclone_alert.clear()
            print("[gateway] cyclone alert cleared -> standard QoS restored")

        _priority, _order, record = pq.get()
        traffic_class = record["traffic_class"]

        if traffic_class == TRAFFIC_CRITICAL:
            sock.sendto(encode(record), (HOST, GATEWAY_TO_SERVER_PORT))
            print(f"[gateway] CRITICAL  {record['node']} seq={record['seq']} forwarded immediately")
        else:
            if cyclone_alert.is_set():
                time.sleep(0.5)  # reserve bandwidth for critical traffic
            sock.sendto(encode(record), (HOST, GATEWAY_TO_SERVER_PORT))
            note = "  (throttled - alert active)" if cyclone_alert.is_set() else ""
            print(f"[gateway] normal     {record['node']} seq={record['seq']} forwarded{note}")


if __name__ == "__main__":
    threading.Thread(target=receiver, daemon=True).start()
    qos_forwarder()
