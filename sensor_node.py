"""
Sensor Node Simulator
----------------------
Emulates an ocean buoy / coastal radar sending lightweight telemetry
(MQTT/CoAP-style compact JSON record) over a UDP socket toward the edge
gateway (spec section 9.2).

* Readings come from the cyclone physics model in ocean_model.py: after
  `--cyclone-after` seconds a vortex approaches, wind rises and pressure
  falls, then the storm passes and conditions recover.
* `--loss` drops packets before sending to emulate a lossy marine /
  satellite link. `--burst` (0..1) makes the losses bursty (Gilbert-Elliott
  rain-fade model) instead of independent coin flips (spec 9.5).
* Every `--housekeeping-every` readings a NON_ESSENTIAL diagnostics packet
  (battery, RSSI) is also sent, so the gateway QoS has three classes.
* `--truth-log file.csv` records every generated reading, including the
  ones that were "lost", so evaluate.py can measure reconstruction error.

A real ESP32 node (hardware/esp32_buoy) sends exactly the same JSON format,
so it can replace this script without changing anything downstream.

Usage:
    python sensor_node.py --node BUOY_07 --loss 0.1
    python sensor_node.py --node RADAR_COAST_A --loss 0.15 --cyclone-after 15
"""
import argparse
import csv
import random
import socket
import time
import zlib

from common import (
    GATEWAY_HOST,
    SENSOR_TO_GATEWAY_PORT,
    encode,
    make_housekeeping,
    make_telemetry,
)
from ocean_model import CycloneParams, GilbertElliottLink, OceanNode


def run_sensor(node_id, loss_rate, interval, cyclone_after, burst=0.0, gateway_host=GATEWAY_HOST,
               gateway_port=SENSOR_TO_GATEWAY_PORT, cyclone_speed=10.0, closest_km=25.0,
               housekeeping_every=5, truth_log=None, seed=None, max_packets=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seed = seed if seed is not None else zlib.crc32(node_id.encode()) & 0xFFFF
    rng = random.Random(seed)

    onset_step = int(cyclone_after / interval) if cyclone_after else 0
    params = CycloneParams(onset_step=onset_step, speed_km_per_step=cyclone_speed * interval,
                           closest_km=closest_km, enabled=bool(cyclone_after))
    ocean = OceanNode(params, seed=seed, steps_per_day=int(240 / max(interval, 1e-3)))
    link = GilbertElliottLink(loss_rate, burstiness=burst, seed=seed + 1) if burst > 0 else None

    truth_file = open(truth_log, "w", newline="") if truth_log else None
    truth_writer = csv.writer(truth_file) if truth_file else None
    if truth_writer:
        truth_writer.writerow(["node", "seq", "wind", "temp", "pressure", "lost"])

    print(f"[{node_id}] sensor started -> sending to {gateway_host}:{gateway_port} "
          f"(loss={loss_rate:.0%}{', bursty' if link else ''})")
    seq = 0
    hk_seq = 0
    try:
        while max_packets is None or seq < max_packets:
            seq += 1
            wind, temp, pressure = ocean.step()
            record = make_telemetry(node_id, seq, wind, temp, pressure)

            lost = link.lost() if link else rng.random() < loss_rate
            if truth_writer:
                truth_writer.writerow([node_id, seq, record["wind"], record["temp"], record["pressure"], int(lost)])
                truth_file.flush()

            if lost:
                print(f"[{node_id}] seq={seq:05d} LOST (simulated link loss)")
            else:
                sock.sendto(encode(record), (gateway_host, gateway_port))
                print(f"[{node_id}] seq={seq:05d} wind={record['wind']:6.2f} "
                      f"pressure={record['pressure']:7.2f} sent")

            if housekeeping_every and seq % housekeeping_every == 0:
                hk_seq += 1
                hk = make_housekeeping(node_id, hk_seq, battery_v=3.7 - 0.0005 * seq + rng.gauss(0, 0.01),
                                       rssi=rng.randint(-95, -60))
                sock.sendto(encode(hk), (gateway_host, gateway_port))

            time.sleep(interval)
    finally:
        if truth_file:
            truth_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ocean sensor / radar simulator")
    parser.add_argument("--node", default="BUOY_01", help="Node identifier")
    parser.add_argument("--loss", type=float, default=0.08, help="Simulated packet loss rate (0-1)")
    parser.add_argument("--burst", type=float, default=0.0,
                        help="Loss burstiness 0-1 (0 = independent losses, 0.7 = rain-fade bursts)")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between readings")
    parser.add_argument("--cyclone-after", type=float, default=20.0,
                        help="Seconds after which the cyclone starts approaching (0 to disable)")
    parser.add_argument("--cyclone-speed", type=float, default=10.0, help="Cyclone approach speed, km per second")
    parser.add_argument("--closest-km", type=float, default=25.0, help="Closest approach of the eye to this node")
    parser.add_argument("--housekeeping-every", type=int, default=5,
                        help="Send a NON_ESSENTIAL diagnostics packet every N readings (0 = never)")
    parser.add_argument("--gateway-host", default=GATEWAY_HOST)
    parser.add_argument("--gateway-port", type=int, default=SENSOR_TO_GATEWAY_PORT)
    parser.add_argument("--truth-log", help="CSV file recording every generated reading (incl. lost ones)")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--count", type=int, help="Stop after N readings")
    args = parser.parse_args()
    try:
        run_sensor(args.node, args.loss, args.interval, args.cyclone_after, burst=args.burst,
                   gateway_host=args.gateway_host, gateway_port=args.gateway_port,
                   cyclone_speed=args.cyclone_speed, closest_km=args.closest_km,
                   housekeeping_every=args.housekeeping_every, truth_log=args.truth_log,
                   seed=args.seed, max_packets=args.count)
    except KeyboardInterrupt:
        print(f"[{args.node}] stopped")
