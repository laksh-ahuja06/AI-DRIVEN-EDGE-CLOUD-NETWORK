"""Figures for the individual Review-1 and Review-2 reports.

R1: proposed block diagram with each member's part highlighted.
R2: flowchart of each member's prototype module + plots from a re-run of the
    Review-2 prototype (commit 82bcb8a, logs in docs/reports/evidence/r2_prototype).

Run from the repository root: python docs/reports/make_r1r2_figures.py
"""
import os
import re
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "fig")
EV = os.path.join(HERE, "evidence", "r2_prototype")
ASSETS = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5})
K, BLUE, HL, GREY = "#1f2937", "#2F5D8A", "#FDE68A", "#F3F4F6"


def canvas(w=8, h=4.6):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w * 10)
    ax.set_ylim(0, h * 10)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, fc="white", bold=False, fs=8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=1", fc=fc, ec=K, lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal")


def diamond(ax, cx, cy, w, h, text):
    ax.add_patch(Polygon([(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
                         fc="white", ec=K, lw=1))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=7.6)


def arr(ax, x1, y1, x2, y2, label=None, dashed=False, lx=0, ly=0.9):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=10, lw=1, color=K,
                                 ls=(0, (4, 2)) if dashed else "-"))
    if label:
        ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, ha="center", fontsize=7, color="#374151")


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=190, facecolor="white", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


# ---------------------------------------------------------------- R1 proposal diagrams
OWN = {"laksh": {"server", "dash", "qos", "net"},
       "anvay": {"gw", "edgeai", "ml"},
       "sreehari": {"sensors", "sat", "hw", "recover"}}


def r1_diagram(who):
    o = OWN[who]
    c = lambda k: HL if k in o else GREY  # noqa: E731
    fig, ax = canvas(8, 4.4)
    ax.text(40, 42.5, "Proposed system (Review 1) — my parts highlighted", ha="center", fontsize=10, fontweight="bold")
    box(ax, 2, 28, 17, 8, "Ocean buoys &\ncoastal radars\n(simulated)", c("sensors"))
    box(ax, 2, 17, 17, 8, "Satellite ground\nstation", c("sat"))
    box(ax, 2, 6, 17, 8, "Low-cost hardware\nnodes (ESP32, later)", c("hw"))
    box(ax, 27, 26, 18, 10, "Edge gateway:\nclassify traffic\n(CRITICAL / NORMAL)", c("gw"))
    box(ax, 27, 14, 18, 8, "Priority scheduling\non slow link (QoS)", c("qos"))
    box(ax, 27, 4, 18, 7, "Edge image analysis\n+ ML early warning", c("edgeai"))
    box(ax, 53, 24, 17, 12, "Central server:\nrisk score + API", c("server"))
    box(ax, 53, 12, 17, 8, "Recover lost\nreadings", c("recover"))
    box(ax, 53, 2, 17, 7, "Time-series model\n(LSTM, planned)", c("ml"))
    box(ax, 72.5, 26, 7, 8, "Dash-\nboard", c("dash"), fs=7.5)
    box(ax, 27, 38, 43, 3.2, "Network topology emulation (Cisco Packet Tracer)", c("net"), fs=7.5)
    arr(ax, 19, 32, 27, 31, "UDP")
    arr(ax, 19, 21, 27, 29)
    arr(ax, 19, 10, 27, 27.5)
    arr(ax, 36, 26, 36, 22)
    arr(ax, 45, 18, 53, 28, "priority\norder", lx=-1, ly=1.5)
    arr(ax, 70, 30, 72.5, 30)
    arr(ax, 61.5, 24, 61.5, 20)
    arr(ax, 61.5, 12, 61.5, 9)
    arr(ax, 19, 19, 27, 8, dashed=True)
    save(fig, f"R1_{who}_proposal.png")


# ---------------------------------------------------------------- R2 flowcharts (prototype modules)
def flow(name, title, steps, branches=None, extra=None):
    """branches: {step_index: text} side box to the right of that (diamond) step."""
    fig, ax = canvas(7.4, 7.2)
    ax.text(37, 70, title, ha="center", fontsize=10, fontweight="bold")
    cx, y = 24, 64
    prev = None
    for idx, (kind, text) in enumerate(steps):
        h = 6.5 if kind == "dia" else 5.6
        top = y + h / 2
        if prev is not None:
            arr(ax, cx, prev, cx, top)
        if kind == "dia":
            diamond(ax, cx, y, 22, h, text)
        else:
            box(ax, cx - 16, y - h / 2, 32, h, text, "#EEF4FB" if kind == "io" else "white")
        if branches and idx in branches:
            box(ax, 50, y - 3.2, 22, 6.4, branches[idx], "#FFF7ED", fs=7.4)
            arr(ax, cx + (11 if kind == "dia" else 16), y, 50, y, dashed=True)
        prev = y - h / 2
        y -= h + 2.3
    for (sx, sy, sw, sh, text) in (extra or []):
        box(ax, sx, sy, sw, sh, text, "#FFF7ED", fs=7.4)
    save(fig, name)


def r2_flows():
    flow("R2_laksh_server_flow.png", "Central server prototype (central_server.py, R2)", [
        ("io", "FastAPI startup event starts the\nUDP listener thread (port 9002)"),
        ("box", "Receive datagram from gateway, decode JSON"),
        ("dia", "seq − last_seq > 1 ?"),
        ("box", "Call reconstruct_gap(): fill missing seq\n(team interpolation baseline), mark reconstructed"),
        ("box", "risk = 100·(0.6·min(1, wind/60) +\n0.4·pressure depression towards 990 hPa)"),
        ("box", "Append to node deque (last 50); update stats\n(received / reconstructed / critical)"),
        ("io", "REST: /predict  /status  /telemetry/{node}\nalert if max risk ≥ 60"),
        ("io", "HTML dashboard polls /predict every 2 s"),
    ], branches={2: "no → skip\nreconstruction"})
    flow("R2_anvay_gateway_flow.png", "Edge gateway prototype (edge_gateway.py, R2)", [
        ("io", "Receiver thread: UDP port 9001"),
        ("box", "Decode JSON record from sensor node"),
        ("dia", "wind ≥ 60 km/h or\npressure ≤ 990 hPa ?"),
        ("box", "CRITICAL: priority 0, set cyclone alert,\nremember time of last critical packet"),
        ("box", "Push (priority, order, record) into\nPriorityQueue (CRITICAL served first)"),
        ("box", "Forwarder thread: take highest priority;\nclear alert after 10 s without critical"),
        ("dia", "NORMAL and\nalert active ?"),
        ("io", "Forward to server, UDP port 9002"),
    ], branches={2: "no → NORMAL,\npriority 1", 6: "yes → sleep 0.5 s\n(throttle), then send"})
    flow("R2_sreehari_sensor_flow.png", "Sensor node + gap filling (R2 prototype)", [
        ("io", "Start: wind 15 km/h, temp 28 °C,\npressure 1008 hPa, seq = 0"),
        ("box", "Every 1 s: seq = seq + 1"),
        ("dia", "elapsed > cyclone_after ?"),
        ("box", "Cyclone: wind += U(0.5, 3) (max 120),\npressure −= U(0.2, 1.5) (min 930)"),
        ("box", "Build compact JSON record\n(node, seq, time, wind, temp, pressure)"),
        ("dia", "random() < loss rate ?"),
        ("io", "Send over UDP to gateway (port 9001)"),
    ], branches={2: "no → small random\nwalk (calm sea)", 5: "yes → packet LOST\n(not sent)"},
       extra=[(47, 2, 26, 11, "Server-side gap filling\n(my reconstruct_gap):\nx_k = x_prev + (k/gap)\n·(x_curr − x_prev)")])


# ---------------------------------------------------------------- R2 evidence plots (re-run of prototype)
def plot_status():
    txt = open(os.path.join(EV, "api.log")).read()
    rows = re.findall(r"t=(\d+)s status: .*?\"received\":(\d+),\"reconstructed\":(\d+),\"critical\":(\d+)", txt)
    risk = re.findall(r"t=(\d+)s predict: \{'overall_risk': ([\d.]+), 'alert': (\w+)", txt)
    t = np.array([int(r[0]) for r in rows])
    fig, ax = plt.subplots(figsize=(6.6, 2.8))
    w = 3.2
    for i, (lab, col) in enumerate((("received", BLUE), ("reconstructed", "#E07B39"), ("critical", "#C0392B"))):
        ax.bar(t + (i - 1) * w, [int(r[i + 1]) for r in rows], w, color=col, label=lab)
    for (tt, rk, al) in risk:
        ax.text(int(tt), 178, f"risk {float(rk):.0f}\n{'ALERT' if al == 'True' else 'normal'}", ha="center", fontsize=7)
    ax.set_ylim(0, 205)
    ax.set_xticks(t, [f"{x} s" for x in t])
    ax.set_ylabel("packets")
    ax.legend(fontsize=7.5, frameon=False, loc="center left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("R2 prototype re-run: /status and /predict polled at 12, 30, 45, 60 s", fontsize=9)
    fig.tight_layout()
    save(fig, "R2_laksh_status.png")


def plot_gateway():
    lines = [ln for ln in open(os.path.join(EV, "gateway.log")) if "forwarded" in ln]
    seqs = [(int(re.search(r"seq=(\d+)", ln).group(1)), "CRITICAL" in ln, "throttled" in ln) for ln in lines]
    bins = np.arange(0, 70, 10)
    crit = np.histogram([s for s, c, _ in seqs if c], bins)[0]
    norm = np.histogram([s for s, c, th in seqs if not c and not th], bins)[0]
    thr = np.histogram([s for s, c, th in seqs if th], bins)[0]
    x = bins[:-1] + 5
    fig, ax = plt.subplots(figsize=(6.6, 2.8))
    ax.bar(x, norm, 7, color=BLUE, label="NORMAL (no alert)")
    ax.bar(x, thr, 7, bottom=norm, color="#9CA3AF", label="NORMAL throttled 0.5 s (alert)")
    ax.bar(x, crit, 7, bottom=norm + thr, color="#C0392B", label="CRITICAL (sent first)")
    ax.set_xticks(x, [f"{b}–{b + 9}" for b in bins[:-1]])
    ax.set_ylim(0, 44)
    ax.set_xlabel("sequence number (≈ seconds since start)")
    ax.set_ylabel("packets forwarded")
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("R2 prototype re-run: gateway classification over time (gateway.log)", fontsize=9)
    fig.tight_layout()
    save(fig, "R2_anvay_gateway.png")


def plot_sensor():
    seq, wind, pres, lost = [], [], [], []
    for ln in open(os.path.join(EV, "buoy_07.log")):
        m = re.search(r"seq=(\d+) wind=\s*([\d.]+) pressure=\s*([\d.]+)", ln)
        if m:
            seq.append(int(m.group(1)))
            wind.append(float(m.group(2)))
            pres.append(float(m.group(3)))
        m = re.search(r"seq=(\d+) LOST", ln)
        if m:
            lost.append(int(m.group(1)))
    fig, ax = plt.subplots(figsize=(6.6, 2.8))
    ax.plot(seq, wind, color=BLUE, lw=1.3, label="wind (km/h)")
    ax.axhline(60, color=BLUE, ls=":", lw=1)
    for s in lost:
        ax.axvline(s, color="#C0392B", lw=1, alpha=0.6)
    ax.set_xlabel("sequence number (BUOY_07, 1 reading per second; red lines = LOST)")
    ax.set_ylabel("wind (km/h)", color=BLUE)
    ax2 = ax.twinx()
    ax2.plot(seq, pres, color="#2E8B57", lw=1.3)
    ax2.axhline(990, color="#2E8B57", ls=":", lw=1)
    ax2.set_ylabel("pressure (hPa)", color="#2E8B57")
    ax.set_title("R2 prototype re-run: my sensor node's output (buoy_07.log)", fontsize=9)
    fig.tight_layout()
    save(fig, "R2_sreehari_sensor.png")


def copy_packet_tracer():
    src = os.path.join(os.path.dirname(HERE), "patent", "assets", "packet_tracer.png")
    os.makedirs(ASSETS, exist_ok=True)
    shutil.copy(src, os.path.join(ASSETS, "pt_topology.png"))


if __name__ == "__main__":
    for w in OWN:
        r1_diagram(w)
    r2_flows()
    plot_status()
    plot_gateway()
    plot_sensor()
    copy_packet_tracer()
    print(sorted(f for f in os.listdir(OUT) if f.startswith("R")))
