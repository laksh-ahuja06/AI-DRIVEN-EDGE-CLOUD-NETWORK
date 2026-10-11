"""
One-command demo: starts the central server, the edge gateway, three
simulated sensor nodes and a satellite ground station as subprocesses in
one process group (this avoids the "background processes lost their
working directory" problem from Review 1), then prints a summary.

Usage:
    python run_demo.py                 # runs until Ctrl+C, dashboard at http://127.0.0.1:8000
    python run_demo.py --duration 90   # stop automatically and print results
    python run_demo.py --no-sensors    # only server + gateway (use with ESP32 hardware nodes)
    python run_demo.py --scheduler fifo --policy rule   # baseline comparison

Logs from every component go to logs/<name>.log.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))


def start(name, args, env, log_dir):
    log = open(os.path.join(log_dir, f"{name}.log"), "w")
    proc = subprocess.Popen([sys.executable, *args], cwd=HERE, env=env, stdout=log, stderr=subprocess.STDOUT)
    print(f"  started {name:<14} pid={proc.pid}  -> logs/{name}.log")
    return proc


def fetch(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=3) as resp:
        return json.loads(resp.read())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=float, default=0, help="Seconds to run (0 = until Ctrl+C)")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--policy", default="hybrid", choices=["rule", "ml", "hybrid"])
    parser.add_argument("--scheduler", default="priority", choices=["priority", "fifo"])
    parser.add_argument("--backbone-bps", type=int, default=1200)
    parser.add_argument("--loss", type=float, default=0.12)
    parser.add_argument("--burst", type=float, default=0.6)
    parser.add_argument("--cyclone-after", type=float, default=15)
    parser.add_argument("--recon", default="lstm", choices=["lstm", "linear"])
    parser.add_argument("--no-sensors", action="store_true", help="Only start server + gateway (for hardware nodes)")
    args = parser.parse_args()

    log_dir = os.path.join(HERE, "logs")
    os.makedirs(log_dir, exist_ok=True)
    env = dict(os.environ, PYTHONUNBUFFERED="1", RECON_METHOD=args.recon)

    print("Starting AI-driven edge-cloud cyclone network demo")
    procs = [start("server", ["-m", "uvicorn", "central_server:app", "--host", "0.0.0.0", "--port", str(args.port),
                              "--log-level", "warning"], env, log_dir)]
    for _ in range(50):  # wait until the API is up
        try:
            fetch(args.port, "/health")
            break
        except OSError:
            time.sleep(0.2)
    procs.append(start("gateway", ["edge_gateway.py", "--policy", args.policy, "--scheduler", args.scheduler,
                                   "--backbone-bps", str(args.backbone_bps)], env, log_dir))
    time.sleep(0.5)
    if not args.no_sensors:
        common = ["--loss", str(args.loss), "--burst", str(args.burst)]
        procs.append(start("buoy_07", ["sensor_node.py", "--node", "BUOY_07", "--cyclone-after",
                                       str(args.cyclone_after), "--closest-km", "15", "--truth-log",
                                       "logs/truth_BUOY_07.csv", *common], env, log_dir))
        procs.append(start("buoy_12", ["sensor_node.py", "--node", "BUOY_12", "--cyclone-after",
                                       str(args.cyclone_after + 5), "--closest-km", "80", "--truth-log",
                                       "logs/truth_BUOY_12.csv", *common], env, log_dir))
        procs.append(start("radar_a", ["sensor_node.py", "--node", "RADAR_COAST_A", "--cyclone-after",
                                       str(args.cyclone_after + 10), "--closest-km", "40", "--truth-log",
                                       "logs/truth_RADAR_COAST_A.csv", *common], env, log_dir))
        procs.append(start("satellite", ["satellite_station.py", "--node", "SAT_GS_01", "--interval", "3",
                                         "--cyclone-after", str(max(0.0, args.cyclone_after - 10)), "--ramp", "40"],
                           env, log_dir))
    print(f"\nDashboard: http://127.0.0.1:{args.port}   (Ctrl+C to stop)\n")

    def shutdown(*_):
        for p in procs:
            if p.poll() is None:
                p.send_signal(signal.SIGINT)
        time.sleep(0.5)
        for p in procs:
            if p.poll() is None:
                p.kill()

    try:
        t0 = time.time()
        while not args.duration or time.time() - t0 < args.duration:
            time.sleep(5)
            try:
                pred = fetch(args.port, "/predict")
                st = fetch(args.port, "/status")["stats"]
                print(f"[{time.time() - t0:5.0f}s] risk={pred['overall_risk']:5.1f} alert={pred['alert']!s:5} "
                      f"rx={st['received']} reconstructed={st['reconstructed']} concealed={st['concealed']} "
                      f"critical={st['critical']}")
            except OSError as exc:
                print(f"server not reachable: {exc}")
            dead = [p for p in procs if p.poll() is not None]
            if dead:
                print("a component exited early - check logs/:", [p.args for p in dead])
                break
        if args.duration:
            print("\nFinal metrics:")
            print(json.dumps(fetch(args.port, "/metrics"), indent=2))
            print(json.dumps(fetch(args.port, "/gateway"), indent=2))
    except KeyboardInterrupt:
        pass
    finally:
        shutdown()


if __name__ == "__main__":
    main()
