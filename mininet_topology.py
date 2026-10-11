"""
Mininet emulation of the multi-tier WAN (spec 9.8, Appendix B) - OPTIONAL.

Runs the *real* Python components on emulated hosts connected by links
with realistic bandwidth, delay and loss (Linux netem), mirroring the
Cisco Packet Tracer topology from Review 1:

    buoy1, buoy2 --[marine link: 1 Mbps, 20 ms, 8% loss]--+
    radar1       --[coastal link: 2 Mbps, 5 ms, 2% loss]--+-- s_edge (gw) --[backbone: 64 kbps, 30 ms]-- s_dc (server)
    sat1         --[GEO satellite: 1 Mbps, 270 ms, 3% loss]+

All hosts share one 10.0.0.0/24 L2 network (a simplification of the
routed Packet Tracer design - routing is already demonstrated there; this
script focuses on link impairments). Packet loss comes from netem, so the
sensors run with --loss 0.

Requirements: Linux (or an Ubuntu VM), `sudo apt install mininet`, and the
project's Python requirements installed for root
(`sudo pip install -r requirements.txt`).

Usage:
    sudo python3 mininet_topology.py                 # interactive Mininet CLI
    sudo python3 mininet_topology.py --duration 90   # run, print /status, exit

Note: written against the Mininet 2.3 API; it could not be executed in the
environment this project was developed in (no Mininet kernel support), so
treat the first run as a test.
"""
import argparse
import json
import os
import sys
import time

from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSBridge

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
GW_IP, SERVER_IP = "10.0.0.10", "10.0.0.20"


def build():
    net = Mininet(switch=OVSBridge, controller=None, link=TCLink, autoSetMacs=True)
    s_ocean, s_coast, s_sat = net.addSwitch("s1"), net.addSwitch("s2"), net.addSwitch("s3")
    s_edge, s_dc = net.addSwitch("s4"), net.addSwitch("s5")

    buoy1 = net.addHost("buoy1", ip="10.0.0.11/24")
    buoy2 = net.addHost("buoy2", ip="10.0.0.12/24")
    radar1 = net.addHost("radar1", ip="10.0.0.21/24")
    sat1 = net.addHost("sat1", ip="10.0.0.31/24")
    gw = net.addHost("gw", ip=f"{GW_IP}/24")
    server = net.addHost("server", ip=f"{SERVER_IP}/24")

    for h in (buoy1, buoy2):
        net.addLink(h, s_ocean)
    net.addLink(radar1, s_coast)
    net.addLink(sat1, s_sat)
    net.addLink(gw, s_edge)
    net.addLink(server, s_dc)

    net.addLink(s_ocean, s_edge, bw=1, delay="20ms", loss=8)      # lossy marine radio link
    net.addLink(s_coast, s_edge, bw=2, delay="5ms", loss=2)       # coastal microwave link
    net.addLink(s_sat, s_edge, bw=1, delay="270ms", loss=3)       # geostationary satellite hop
    net.addLink(s_edge, s_dc, bw=0.064, delay="30ms")             # constrained backbone (64 kbps)
    return net


def start_apps(net, backbone_bps):
    os.makedirs(os.path.join(HERE, "logs"), exist_ok=True)
    env = f"cd {HERE} && GATEWAY_HOST={GW_IP} SERVER_HOST={SERVER_IP} PYTHONUNBUFFERED=1"
    net["server"].cmd(f"{env} {PY} -m uvicorn central_server:app --host 0.0.0.0 --port 8000 "
                      f"> logs/mn_server.log 2>&1 &")
    time.sleep(3)
    net["gw"].cmd(f"{env} {PY} edge_gateway.py --backbone-bps {backbone_bps} > logs/mn_gateway.log 2>&1 &")
    time.sleep(1)
    sensors = [("buoy1", "BUOY_01", 15, 15), ("buoy2", "BUOY_02", 20, 60), ("radar1", "RADAR_01", 25, 35)]
    for host, node, after, closest in sensors:
        net[host].cmd(f"{env} {PY} sensor_node.py --node {node} --loss 0 --cyclone-after {after} "
                      f"--closest-km {closest} --gateway-host {GW_IP} > logs/mn_{host}.log 2>&1 &")
    net["sat1"].cmd(f"{env} {PY} satellite_station.py --node SAT_GS_01 --cyclone-after 5 "
                    f"--gateway-host {GW_IP} > logs/mn_sat1.log 2>&1 &")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=float, default=0)
    parser.add_argument("--backbone-bps", type=int, default=1200)
    args = parser.parse_args()
    setLogLevel("info")
    net = build()
    net.start()
    try:
        print(net["buoy1"].cmd(f"ping -c 3 {SERVER_IP}"))
        start_apps(net, args.backbone_bps)
        print(f"Apps started. Dashboard inside Mininet: server at http://{SERVER_IP}:8000 "
              f"(e.g. `mininet> buoy1 curl -s {SERVER_IP}:8000/status`)")
        if args.duration:
            time.sleep(args.duration)
            out = net["buoy1"].cmd(f"curl -s http://{SERVER_IP}:8000/metrics")
            try:
                print(json.dumps(json.loads(out), indent=2))
            except ValueError:
                print(out)
        else:
            CLI(net)
    finally:
        for h in net.hosts:
            h.cmd("pkill -f sensor_node.py; pkill -f satellite_station.py; pkill -f edge_gateway.py; "
                  "pkill -f 'uvicorn central_server'")
        net.stop()


if __name__ == "__main__":
    main()
