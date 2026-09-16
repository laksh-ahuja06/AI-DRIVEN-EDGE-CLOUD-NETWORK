"""
Sensor Node Simulator
----------------------
Emulates an ocean buoy / coastal radar / satellite ground station
sending lightweight telemetry (MQTT/CoAP-style compact record) over a
UDP socket toward the edge gateway. A configurable loss rate simulates
a lossy marine/satellite link (spec section 9.2, 9.5).

After `--cyclone-after` seconds, wind rises and pressure drops to
simulate a developing cyclone, which should trigger AI-driven QoS
prioritization and a rising risk score on the central server.

Usage:
    python sensor_node.py --node BUOY_07 --loss 0.1
    python sensor_node.py --node RADAR_COAST_A --loss 0.15 --cyclone-after 15
"""
import argparse
import random
import socket
import time

from common import HOST, SENSOR_TO_GATEWAY_PORT, make_telemetry, encode


def run_sensor(node_id, loss_rate, interval, cyclone_after):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq = 0

    # Baseline "calm sea" conditions
    wind, temp, pressure = 15.0, 28.0, 1008.0

    print(f"[{node_id}] sensor started -> sending to {HOST}:{SENSOR_TO_GATEWAY_PORT}")
    start = time.time()

    while True:
        seq += 1
        elapsed = time.time() - start

        if cyclone_after and elapsed > cyclone_after:
            wind = min(120.0, wind + random.uniform(0.5, 3.0))
            pressure = max(930.0, pressure - random.uniform(0.2, 1.5))
        else:
            wind = max(0.0, wind + random.uniform(-1.0, 1.0))
            pressure += random.uniform(-0.5, 0.5)
        temp += random.uniform(-0.2, 0.2)

        record = make_telemetry(node_id, seq, wind, temp, pressure)

        # Simulate a lossy link: some packets never arrive at the gateway.
        if random.random() < loss_rate:
            print(f"[{node_id}] seq={seq:05d} LOST (simulated link loss)")
        else:
            sock.sendto(encode(record), (HOST, SENSOR_TO_GATEWAY_PORT))
            print(f"[{node_id}] seq={seq:05d} wind={record['wind']:6.2f} "
                  f"pressure={record['pressure']:7.2f} sent")

        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ocean sensor / radar simulator")
    parser.add_argument("--node", default="BUOY_01", help="Node identifier")
    parser.add_argument("--loss", type=float, default=0.08, help="Simulated packet loss rate (0-1)")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between readings")
    parser.add_argument("--cyclone-after", type=float, default=20.0,
                         help="Seconds after which conditions worsen (0 to disable)")
    args = parser.parse_args()
    run_sensor(args.node, args.loss, args.interval, args.cyclone_after)
