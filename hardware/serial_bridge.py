"""
Serial -> UDP bridge for the optional LoRa link.

Reads the CSV lines printed by hardware/lora_receiver (node,seq,wind,temp,
pressure,rssi,snr), converts them to the project's JSON telemetry format
and forwards them to edge_gateway.py over UDP. Lines starting with '#' are
status messages and are only printed.

Usage:
    pip install pyserial
    python hardware/serial_bridge.py --port /dev/ttyUSB0        # Linux / Raspberry Pi
    python hardware/serial_bridge.py --port COM3                # Windows
    python hardware/serial_bridge.py --stdin < recorded.csv     # replay without hardware
"""
import argparse
import os
import socket
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import GATEWAY_HOST, SENSOR_TO_GATEWAY_PORT, encode, make_housekeeping, make_telemetry  # noqa: E402

NODE_PREFIX = {"B": "BUOY_LORA_", "R": "RADAR_LORA_"}


def parse_line(line):
    """Returns (telemetry_record, housekeeping_record) or None for a bad line."""
    parts = line.strip().split(",")
    if len(parts) < 5 or line.startswith("#"):
        return None
    try:
        node, seq = parts[0], int(parts[1])
        wind, temp, pressure = (float(x) for x in parts[2:5])
    except ValueError:
        return None
    node_id = NODE_PREFIX.get(node[:1], "NODE_") + node[1:] if node[:1] in NODE_PREFIX else node
    rec = make_telemetry(node_id, seq, wind, temp, pressure)
    rec["link"] = "lora"
    hk = None
    if len(parts) >= 7:
        try:
            rssi, snr = int(float(parts[5])), float(parts[6])
            hk = make_housekeeping(node_id, seq, battery_v=0.0, rssi=rssi)
            hk["snr"] = snr
        except ValueError:
            pass
    return rec, hk


def lines_from_serial(port, baud):
    import serial  # pyserial
    with serial.Serial(port, baud, timeout=1) as ser:
        print(f"[bridge] reading {port} @ {baud} baud")
        while True:
            raw = ser.readline()
            if raw:
                yield raw.decode("utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", help="Serial port of the LoRa receiver ESP32")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--stdin", action="store_true", help="Read CSV lines from stdin instead")
    parser.add_argument("--gateway-host", default=GATEWAY_HOST)
    parser.add_argument("--gateway-port", type=int, default=SENSOR_TO_GATEWAY_PORT)
    parser.add_argument("--hk-every", type=int, default=5, help="Forward link-quality housekeeping every N packets")
    args = parser.parse_args()
    if not args.stdin and not args.port:
        parser.error("give --port or --stdin")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    source = sys.stdin if args.stdin else lines_from_serial(args.port, args.baud)
    count = 0
    try:
        for line in source:
            if line.startswith("#"):
                print(line.strip())
                continue
            parsed = parse_line(line)
            if parsed is None:
                print(f"[bridge] ignored: {line.strip()!r}")
                continue
            rec, hk = parsed
            sock.sendto(encode(rec), (args.gateway_host, args.gateway_port))
            count += 1
            if hk and args.hk_every and count % args.hk_every == 0:
                sock.sendto(encode(hk), (args.gateway_host, args.gateway_port))
            print(f"[bridge] {rec['node']} seq={rec['seq']} wind={rec['wind']} pressure={rec['pressure']} -> gateway")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
