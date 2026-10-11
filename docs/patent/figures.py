"""Patent-style black-and-white drawings for the complete specification.

Run from the repository root: python docs/patent/figures.py && python docs/patent/build_spec.py
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle, Polygon
from PIL import Image, ImageOps

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig")
ORIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.linewidth": 0.8,
                     "hatch.linewidth": 0.6})
K = "black"


def canvas(w=8.0, h=5.6):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w * 10)
    ax.set_ylim(0, h * 10)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, num=None, lw=1.1, fs=8.5, dashed=False, rounded=False, numpos="tr", bold=False):
    style = "round,pad=0.0,rounding_size=1.2" if rounded else "square,pad=0"
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style, fill=False, ec=K, lw=lw,
                                ls=(0, (4, 2)) if dashed else "-"))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, wrap=True,
            fontweight="bold" if bold else "normal")
    if num is not None:
        if numpos == "tr":
            ax.annotate(str(num), xy=(x + w, y + h), xytext=(x + w + 2.5, y + h + 2.2), fontsize=8,
                        arrowprops=dict(arrowstyle="-", lw=0.6, color=K))
        elif numpos == "tl":
            ax.annotate(str(num), xy=(x, y + h), xytext=(x - 5.5, y + h + 2.2), fontsize=8,
                        arrowprops=dict(arrowstyle="-", lw=0.6, color=K))
        elif numpos == "br":
            ax.annotate(str(num), xy=(x + w, y), xytext=(x + w + 2.5, y - 3.2), fontsize=8,
                        arrowprops=dict(arrowstyle="-", lw=0.6, color=K))
        elif numpos == "bl":
            ax.annotate(str(num), xy=(x, y), xytext=(x - 5.5, y - 3.2), fontsize=8,
                        arrowprops=dict(arrowstyle="-", lw=0.6, color=K))


def arrow(ax, x1, y1, x2, y2, text=None, both=False, dashed=False, tx=0, ty=1.6, fs=7.5, rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="<|-|>" if both else "-|>",
                                 mutation_scale=9, lw=0.9, color=K, ls=(0, (4, 2)) if dashed else "-",
                                 connectionstyle=f"arc3,rad={rad}"))
    if text:
        ax.text((x1 + x2) / 2 + tx, (y1 + y2) / 2 + ty, text, ha="center", va="bottom", fontsize=fs)


def diamond(ax, cx, cy, w, h, text, fs=7.8):
    ax.add_patch(Polygon([(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
                         fill=False, ec=K, lw=1.0))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs)


def title(ax, t, y=None):
    y = y if y is not None else ax.get_ylim()[1] - 3
    ax.text(ax.get_xlim()[1] / 2, y, t, ha="center", va="top", fontsize=11, fontweight="bold")


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=220, facecolor="white")
    plt.close(fig)


# ---------------------------------------------------------------- FIG 1
def fig1():
    fig, ax = canvas(8, 5.8)
    title(ax, "FIG. 1")
    ax.add_patch(Rectangle((2, 4), 76, 46, fill=False, ec=K, lw=0.7, ls=(0, (6, 3))))
    ax.text(3.5, 47.5, "100", fontsize=8)
    for k, (t, n) in enumerate([("Ocean buoy\nsensor node", 110), ("Coastal radar\nsensor node", 112),
                                ("Satellite ground\nstation + edge AI", 114), ("Hardware node\n(MCU + sensors)", 116)]):
        box(ax, 9, 36 - 10 * k, 15, 7, t, n, numpos="tl")
    for y in (39.5, 29.5, 19.5):
        arrow(ax, 24, y, 32, 24.5 + (y - 24.5) * 0.25)
    arrow(ax, 24, 10.5, 32, 19)
    arrow(ax, 32, 17, 24, 8.5, dashed=True)
    ax.text(25, 44.5, "lossy links 130", fontsize=7.5)
    ax.text(25.5, 6.0, "alert 260", fontsize=7.2)
    box(ax, 32, 15, 15, 19, "Edge\ngateway\n\nvalidate\nclassify\nQoS schedule", 200)
    arrow(ax, 47, 26, 57, 26, "constrained\nbackbone 300")
    box(ax, 57, 15, 16, 19, "Central\nprediction\nserver\n\nreconstruct\nfuse risk\nforecast", 400)
    arrow(ax, 65, 34, 65, 40)
    box(ax, 57, 40, 16, 6.5, "Dashboard / API", 500)
    arrow(ax, 61, 15, 41, 15, "QoS feedback 460", dashed=True, ty=-5.5, rad=-0.35)
    save(fig, "fig01.png")


# ---------------------------------------------------------------- FIG 2 gateway
def fig2():
    fig, ax = canvas(8, 5.8)
    title(ax, "FIG. 2")
    ax.add_patch(Rectangle((3, 6), 74, 45, fill=False, ec=K, lw=0.8))
    ax.text(5, 48.5, "Edge gateway 200", fontsize=8.5)
    box(ax, 7, 36, 13, 8, "Datagram\nreceiver", 205, numpos="tl")
    box(ax, 24, 36, 13, 8, "Parse /\nvalidate", 210)
    box(ax, 41, 40, 14, 6.5, "Rule\nclassifier", 222)
    box(ax, 41, 30, 14, 6.5, "ML trend\nclassifier", 224, numpos="br")
    box(ax, 24, 22, 13, 7, "Node history\nbuffer", 230, numpos="bl")
    box(ax, 60, 33, 15, 9, "Class decision\n(hybrid OR)", 220)
    arrow(ax, 20, 40, 24, 40)
    arrow(ax, 37, 41, 41, 43)
    arrow(ax, 37, 39, 41, 34)
    arrow(ax, 37, 25.5, 41, 32)
    arrow(ax, 55, 43, 60, 40)
    arrow(ax, 55, 33, 60, 36)
    ax.add_patch(Rectangle((6, 9), 46, 10, fill=False, ec=K, lw=0.9))
    ax.text(7, 17, "QoS scheduler 240", fontsize=7.8)
    for i, lab in enumerate(["CRITICAL", "NORMAL", "NON-ESS."]):
        box(ax, 8 + i * 10.5, 10, 9.5, 5, lab, fs=6.6)
    ax.text(8, 7.0, "per-class queues 242", fontsize=7)
    box(ax, 41, 10, 9.5, 6, "token\nbucket", None, fs=6.8)
    ax.text(39, 7.0, "244 / 246 / 248", fontsize=7)
    arrow(ax, 63, 33, 50, 19)
    box(ax, 60, 21, 15, 7, "Alert\ncontroller", 250, numpos="br")
    box(ax, 60, 9, 15, 7, "Node alert\nnotifier", 260, numpos="br")
    arrow(ax, 70, 33, 70, 28)
    arrow(ax, 67.5, 21, 67.5, 16)
    arrow(ax, 60, 24.5, 52, 16, dashed=True)
    arrow(ax, 29, 9, 29, 1.5)
    ax.text(30, 2.5, "to server 400 via backbone 300", fontsize=7)
    arrow(ax, 67.5, 9, 67.5, 1.5)
    ax.text(68.5, 2.5, "to nodes 116", fontsize=7)
    ax.text(57, 54.5, "QoS feedback from 460", fontsize=7)
    arrow(ax, 78.5, 53, 75, 27, dashed=True, rad=-0.15)
    save(fig, "fig02.png")


# ---------------------------------------------------------------- FIG 3 server
def fig3():
    fig, ax = canvas(8, 5.4)
    title(ax, "FIG. 3")
    ax.add_patch(Rectangle((3, 3), 74, 44, fill=False, ec=K, lw=0.8))
    ax.text(5, 44.5, "Central prediction server 400", fontsize=8.5)
    box(ax, 6, 31, 14, 8, "Datagram\nlistener +\nvalidation", 405, numpos="tl")
    box(ax, 25, 31, 14, 8, "Sequence\ntracker", 410)
    box(ax, 44, 36, 14, 6.5, "Gap\nreconstructor", 420)
    box(ax, 44, 27, 14, 6.5, "Late-packet\nreconciler", 440)
    box(ax, 25, 18, 14, 7, "Real-time\nconcealment", 430, numpos="bl")
    box(ax, 6, 18, 14, 7, "LSTM model\n(numpy)", 700, numpos="tl")
    box(ax, 62, 26, 13, 15, "Time-series\nstore\n(flags:\nreconstructed,\nprovisional,\nlate)", 415)
    box(ax, 44, 8, 14, 9, "Risk fusion\n+ forecast", 450, numpos="br")
    box(ax, 62, 8, 13, 9, "REST +\nWebSocket\nAPI", 470, numpos="br")
    box(ax, 25, 6, 14, 7, "QoS feedback\ntransmitter", 460, numpos="bl")
    arrow(ax, 20, 35, 25, 35)
    arrow(ax, 39, 36, 44, 39)
    arrow(ax, 39, 34, 44, 30)
    arrow(ax, 58, 39, 62, 37)
    arrow(ax, 58, 30, 62, 31)
    arrow(ax, 39, 20.5, 62, 27)
    arrow(ax, 20, 21.5, 25, 21.5)
    ax.text(6, 16, "shared by 420, 430, 450", fontsize=6.8)
    arrow(ax, 68.5, 26, 58, 15)
    arrow(ax, 58, 12.5, 62, 12.5)
    arrow(ax, 44, 10, 39, 9.5)
    arrow(ax, 25, 9.5, 2, 9.5)
    ax.text(3.5, 5.5, "to 200", fontsize=7)
    save(fig, "fig03.png")


# ---------------------------------------------------------------- FIG 4 records
def fig4():
    fig, ax = canvas(8, 6.0)
    title(ax, "FIG. 4")
    rows = [
        ("Sensor telemetry record 140", ["node", "seq", "t_sent", "wind", "temp", "pressure", "kind=sensor"]),
        ("Gateway annotation 215 (appended)", ["traffic_class", "qos_policy", "ml_prob", "t_gw"]),
        ("Edge-feature record 150", ["node", "seq", "cold_frac", "min_bt", "centre", "symmetry", "eye_contrast",
                                     "sat_risk", "risk_flag", "thumb", "raw/sent bytes"]),
        ("Housekeeping record 160", ["node", "seq", "battery_v", "rssi", "kind=housekeeping"]),
        ("QoS feedback message 465", ["type=qos_feedback", "alert", "risk"]),
        ("Node alert message 265", ["type=alert", "alert", "risk"]),
        ("Server estimate record 425", ["seq", "values", "reconstructed", "provisional", "method", "risk"]),
    ]
    y = 52
    for name, fields in rows:
        ax.text(3, y + 1.0, name, fontsize=8, fontweight="bold")
        x = 3
        for f in fields:
            w = max(6.0, 1.05 * len(f) + 1.5)
            if x + w > 77:
                x, y = 3, y - 4.6
            ax.add_patch(Rectangle((x, y - 4.2), w, 4.2, fill=False, ec=K, lw=0.8))
            ax.text(x + w / 2, y - 2.1, f, ha="center", va="center", fontsize=6.6)
            x += w
        y -= 6.9
    save(fig, "fig04.png")


# ---------------------------------------------------------------- FIG 5 gateway flowchart
def fig5():
    fig, ax = canvas(8, 8.0)
    title(ax, "FIG. 5")
    cx = 26
    steps = [
        (70, "S501  Receive datagram from node", "box"),
        (63, "S502  Parse + validate\n(fields, seq, physical ranges)", "box"),
        (55, "valid?", "dia"),
        (47, "S504  Update node history;\ncompute trend features", "box"),
        (40, "S505  Rule class  +  ML probability", "box"),
        (32, "CRITICAL?", "dia"),
        (24, "S507  Refresh alert hold timer;\nset alert state", "box"),
        (17, "S508  Enqueue in class queue\n(shed NON_ESSENTIAL if alert\nand backlog > threshold)", "box"),
        (8.5, "S509  Dequeue: strict priority; non-critical\nneeds size + reserve credit during alert", "box"),
    ]
    prev = None
    for y, t, kind in steps:
        if kind == "box":
            box(ax, cx - 18, y - 3, 36, 6, t, fs=7.6)
            top, bot = y + 3, y - 3
        else:
            diamond(ax, cx, y, 18, 6.5, t)
            top, bot = y + 3.25, y - 3.25
        if prev is not None:
            arrow(ax, cx, prev, cx, top)
        prev = bot
    ax.text(cx + 1, 49.6, "yes", fontsize=7)
    ax.text(cx + 1, 26.7, "yes", fontsize=7)
    arrow(ax, cx + 9, 55, 52, 55)
    box(ax, 52, 52, 22, 6, "S503  Count + drop\ninvalid packet", fs=7.6)
    ax.text(cx + 10, 55.8, "no", fontsize=7)
    ax.plot([cx + 9, 50, 50], [32, 32, 17], color=K, lw=0.9)
    arrow(ax, 50, 17, cx + 18, 17)
    ax.text(cx + 10, 32.8, "no", fontsize=7)
    arrow(ax, cx + 18, 8.5, 52, 8.5)
    box(ax, 52, 5.5, 22, 6, "S510  Transmit on\nbackbone 300", fs=7.6)
    box(ax, 52, 63, 22, 10, "Parallel: every 2 s\nS511 send stats to 400\nS512 resync alert to\nnodes (port 9004)", fs=7.2, dashed=True)
    box(ax, 52, 36, 22, 9, "Parallel: on QoS\nfeedback from 460\nupdate server alert", fs=7.2, dashed=True)
    save(fig, "fig05.png")


# ---------------------------------------------------------------- FIG 6 server flowchart
def fig6():
    fig, ax = canvas(8, 8.0)
    title(ax, "FIG. 6")
    cx = 24
    box(ax, cx - 16, 66, 32, 5.5, "S601  Receive sensor record (node, seq)", fs=7.6)
    diamond(ax, cx, 58, 20, 6.5, "seq <= last_seq ?")
    arrow(ax, cx, 66, cx, 61.25)
    diamond(ax, 58, 58, 18, 6.5, "reboot?\n(seq=1 or far back)", fs=6.8)
    arrow(ax, cx + 10, 58, 49, 58)
    ax.text(cx + 11, 58.8, "yes", fontsize=7)
    box(ax, 50, 44, 22, 8, "S603  If stored copy is\nreconstructed: replace with\nreal value (late recovery);\nelse discard duplicate", fs=6.8)
    arrow(ax, 58, 54.75, 61, 52)
    ax.text(59.5, 53, "no", fontsize=7)
    box(ax, 50, 64, 22, 5, "S602  Reset node stream", fs=7)
    arrow(ax, 58, 61.25, 61, 64)
    ax.text(59.8, 61.8, "yes", fontsize=7)
    ax.plot([72, 76, 76, 40], [66.5, 66.5, 54, 54], color=K, lw=0.8, ls=(0, (3, 2)))
    arrow(ax, 40, 54, cx + 1, 49, dashed=True)
    box(ax, cx - 16, 44, 32, 6, "S604  Remove provisional forecasts\nat the tail of the store", fs=7.6)
    arrow(ax, cx, 54.75, cx, 50)
    ax.text(cx + 1, 51.8, "no", fontsize=7)
    diamond(ax, cx, 36, 20, 6.5, "gap n = seq-last-1\n0 < n <= MAX_GAP ?", fs=6.8)
    arrow(ax, cx, 44, cx, 39.25)
    box(ax, cx - 16, 23, 32, 8, "S606  LSTM forecast f1..f(n+1) from\nrepaired history; correct by\n(k/(n+1))·(x_next - f(n+1)); flag reconstructed", fs=7.0)
    arrow(ax, cx, 32.75, cx, 31)
    ax.text(cx + 1, 31.6, "yes", fontsize=7)
    box(ax, cx - 16, 13, 32, 6, "S607  Update arrival-interval EMA;\nappend record; compute risk", fs=7.6)
    arrow(ax, cx, 23, cx, 19)
    ax.plot([cx + 10, 46, 46], [36, 36, 16], color=K, lw=0.9)
    arrow(ax, 46, 16, cx + 16, 16)
    ax.text(cx + 11, 36.8, "no", fontsize=7)
    box(ax, cx - 16, 3, 32, 6, "S608  Fuse risk, forecast, hysteresis\nalert; publish; send QoS feedback", fs=7.6)
    arrow(ax, cx, 13, cx, 9)
    box(ax, 50, 18, 25, 16, "Concurrent loop (0.25 s)\nS610  If now - last_arrival\n> (2.5 + p)·interval and\np < MAX_PROVISIONAL:\nappend LSTM forecast for\nseq last+p+1, flagged\nprovisional", fs=6.9, dashed=True)
    save(fig, "fig06.png")


# ---------------------------------------------------------------- FIG 7 scheduler / token bucket
def fig7():
    fig, ax = canvas(8, 5.0)
    title(ax, "FIG. 7")
    names = [("CRITICAL queue", 242), ("NORMAL queue", 243), ("NON_ESSENTIAL queue", 245)]
    for i, (n, num) in enumerate(names):
        y = 34 - i * 11
        ax.text(3, y + 6.5, f"{n} ({num})", fontsize=7.8)
        for k in range(6):
            ax.add_patch(Rectangle((3 + k * 4.2, y), 4.0, 5, fill=(k < 4 - i), fc="0.85", ec=K, lw=0.8))
        arrow(ax, 29, y + 2.5, 38, 22)
    ax.text(2.5, 8.5, "Shedding 248: NON_ESSENTIAL rejected at enqueue when alert\nand queued bytes > shed_backlog_s × rate", fontsize=7)
    box(ax, 38, 16, 14, 12, "Strict-priority\nselector\n(head-of-line)", 241)
    arrow(ax, 52, 22, 59, 22)
    # bucket
    ax.add_patch(Polygon([(60, 30), (60, 12), (72, 12), (72, 30)], closed=False, fill=False, ec=K, lw=1.1))
    ax.add_patch(Rectangle((60, 12), 12, 11, fill=True, fc="0.85", ec="none"))
    ax.plot([60, 72], [16.5, 16.5], color=K, lw=0.8, ls=(0, (3, 2)))
    ax.text(73, 16.0, "reserve R\n(246)", fontsize=7)
    ax.text(73, 22.5, "credit\nB(t)", fontsize=7)
    ax.text(44, 34.5, "token bucket 244\nrefill r bytes/s, cap Bmax", fontsize=7)
    arrow(ax, 66, 37, 66, 31)
    arrow(ax, 66, 12, 66, 5)
    ax.text(67, 6.5, "to backbone 300", fontsize=7)
    ax.text(2.5, 2.0, "send p if  B(t) >= size(p) + R·[alert ∧ class(p) ≠ CRITICAL]", fontsize=7.6,
            bbox=dict(fc="white", ec=K, lw=0.6))
    save(fig, "fig07.png")


# ---------------------------------------------------------------- FIG 8 anchored LSTM reconstruction
def fig8():
    from ocean_model import CycloneParams, OceanNode
    from reconstruction import Reconstructor, linear_fill
    rec = Reconstructor("lstm")
    node = OceanNode(CycloneParams(onset_step=5, speed_km_per_step=8, closest_km=15), seed=11)
    tr = np.array(node.trace(100))
    s, n = 80, 5
    hist, nxt, truth = list(tr[:s]), tr[s + n], tr[s:s + n]
    fc = rec.forecast(hist, n + 1)
    fill = rec.fill_gap(hist, nxt, n)
    lin = linear_fill(tr[s - 1], nxt, n)
    v = 2  # pressure
    fig, ax = plt.subplots(figsize=(8, 4.2))
    t = np.arange(s - 14, s + n + 4)
    ax.plot(t, tr[t, v], color=K, lw=1.0, marker="o", ms=3, label="received readings")
    idx = np.arange(s, s + n)
    ax.plot(idx, truth[:, v], ls="none", marker="x", color=K, ms=6, label="lost readings (ground truth)")
    ax.plot(np.r_[s - 1, idx, s + n], np.r_[tr[s - 1, v], lin[:, v], nxt[v]], ls=":", color=K, lw=1.2,
            label="linear interpolation (baseline)")
    ax.plot(np.r_[s - 1, np.arange(s, s + n + 1)], np.r_[tr[s - 1, v], fc[:, v]], ls="--", color="0.45", lw=1.2,
            label="LSTM forecast f_k (before anchoring)")
    ax.plot(np.r_[s - 1, idx, s + n], np.r_[tr[s - 1, v], fill[:, v], nxt[v]], color=K, lw=2.0,
            label="anchored LSTM estimate (420)")
    ax.axvspan(s - 0.5, s + n - 0.5, color="0.9")
    ax.text(s + n / 2 - 0.5, ax.get_ylim()[1] - 0.6, "gap (packets lost)", ha="center", va="top", fontsize=8)
    ax.set_xlabel("sequence number")
    ax.set_ylabel("pressure (hPa)")
    ax.legend(fontsize=7.2, frameon=False, loc="best")
    ax.set_title("FIG. 8", fontweight="bold", fontsize=11)
    fig.tight_layout()
    save(fig, "fig08.png")


# ---------------------------------------------------------------- FIG 9 edge AI image pipeline
def fig9():
    from edge_ai import BAND_IR, IR_SCALE, extract_features
    from satellite_station import SyntheticImager
    im = SyntheticImager(size=384, seed=4)
    fig = plt.figure(figsize=(8, 3.9))
    fig.suptitle("FIG. 9", fontweight="bold", fontsize=11, y=0.98)
    for i, I in enumerate((0.0, 0.5, 0.75, 1.0)):
        img = im.frame(I, (0.47, 0.5), rotation=0.9)
        f = extract_features(img)
        ax = fig.add_axes([0.03 + i * 0.245, 0.36, 0.22, 0.5])
        ir = img[BAND_IR] / IR_SCALE
        ax.imshow(300 - ir, cmap="gray", vmin=0, vmax=110)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"intensity {I:.2f}", fontsize=8)
        ax.text(0.5, -0.06, f"cold cover {100 * f['cold_frac']:.1f}%\nsymmetry {f['symmetry']:.2f}\n"
                f"eye contrast {f['eye_contrast']:.0f} K\nrisk {f['sat_risk']:.0f}  flag {'Y' if f['risk_flag'] else 'N'}",
                transform=ax.transAxes, ha="center", va="top", fontsize=7.3)
    fig.text(0.5, 0.03, "Infrared band of a 4-band, 16-bit frame (raw 1.18 MB at 384 px; 2.10 MB at 512 px)\n"
             "→ feature extractor 620 + risk scorer 630 → edge-feature record 150 of about 1.0 KB",
             ha="center", fontsize=7.5)
    save(fig, "fig09.png")


# ---------------------------------------------------------------- FIG 10 sequence diagram
def fig10():
    fig, ax = canvas(8, 5.8)
    title(ax, "FIG. 10")
    cols = [("Node 116", 8), ("Gateway 200", 30), ("Server 400", 52), ("Dashboard 500", 72)]
    for n, x in cols:
        box(ax, x - 7, 45, 14, 4.5, n, fs=7.6)
        ax.plot([x, x], [45, 3], color=K, lw=0.7, ls=(0, (4, 3)))
    msgs = [
        (8, 30, 41.5, "telemetry (wind rising)"),
        (30, 30, 38.5, None),
        (30, 52, 34.5, "forward CRITICAL first"),
        (52, 72, 34, "risk ≥ 60 → alert"),
        (52, 30, 30, "qos_feedback alert=true"),
        (30, 8, 26, "alert=true (port 9004)"),
        (8, 30, 18, "seq gap (packets lost)"),
        (30, 52, 15, None),
        (52, 72, 11, "reconstructed points"),
    ]
    for x1, x2, y, t in msgs:
        if x1 == x2:
            ax.text(x1 - 1.2, y - 2.0, "classify → CRITICAL;\nalert hold; reserve R", fontsize=6.8, ha="right")
            continue
        arrow(ax, x1, y, x2, y, t, fs=7)
    ax.add_patch(Rectangle((4, 21), 8, 3, fill=True, fc="0.85", ec=K, lw=0.6))
    ax.text(8, 22.5, "LED+buzzer", ha="center", va="center", fontsize=6.5)
    ax.text(53, 16.5, "LSTM gap repair 420", fontsize=6.8)
    save(fig, "fig10.png")


# ---------------------------------------------------------------- FIG 11 hardware node
def fig11():
    fig, ax = canvas(8, 5.6)
    title(ax, "FIG. 11")
    box(ax, 30, 14, 20, 24, "Microcontroller\nwith Wi-Fi\n(ESP32)\n\nseq counter 122\nsea-level\ncorrection\nloss emulation", 118, lw=1.4)
    box(ax, 9, 32, 16, 7, "Temp + pressure\nsensor (BMP280)", 120, numpos="tl")
    box(ax, 9, 21, 16, 7, "Wind: anemometer\n(reed/hall) or knob", 121, numpos="tl")
    box(ax, 9, 10, 16, 7, "Storm-mode\nbutton", 123, numpos="bl")
    box(ax, 56, 32, 16, 7, "Alert LED", 124)
    box(ax, 56, 21, 16, 7, "Buzzer via\ntransistor", 125)
    box(ax, 56, 10, 16, 7, "Battery / solar\n(optional)", 126, numpos="br")
    arrow(ax, 25, 35.5, 30, 32, "I²C", fs=7)
    arrow(ax, 25, 24.5, 30, 24.5, "pulse/ADC", fs=6.6)
    arrow(ax, 25, 13.5, 30, 18, fs=7)
    arrow(ax, 50, 32, 56, 35.5)
    arrow(ax, 50, 24.5, 56, 24.5)
    arrow(ax, 56, 13.5, 50, 18)
    ax.plot([40, 40], [38, 44], color=K, lw=1)
    ax.plot([37, 40, 43], [47, 44, 47], color=K, lw=1)
    ax.text(44, 44.5, "radio link 130 (Wi-Fi UDP, or LoRa 132)", fontsize=7.5)
    ax.text(30, 6, "Hardware sensor node 116", fontsize=8)
    save(fig, "fig11.png")


# ---------------------------------------------------------------- FIG 12 dashboard (grayscale screenshot)
def fig12():
    img = Image.open(os.path.join(REPO, "docs/dashboard.png")).convert("L")
    img = ImageOps.autocontrast(ImageOps.invert(img.crop((0, 0, 1400, 1080))))
    fig = plt.figure(figsize=(8, 6.6))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.9])
    ax.imshow(img, cmap="gray")
    ax.set_xlim(0, 1470)
    ax.axis("off")
    for (x, y, n) in [(1390, 78, "502"), (1390, 170, "504"), (920, 300, "506"), (1385, 400, "508"),
                      (1385, 740, "510"), (700, 960, "512"), (1385, 980, "514")]:
        ax.annotate(n, xy=(x - 30, y), xytext=(x + 15, y), fontsize=8, annotation_clip=False,
                    arrowprops=dict(arrowstyle="-", lw=0.7))
    fig.suptitle("FIG. 12", fontweight="bold", fontsize=11, y=0.985)
    save(fig, "fig12.png")


# ---------------------------------------------------------------- FIG 13/14 results (B&W)
def fig13_14():
    import json
    r = json.load(open(os.path.join(REPO, "results/results.json")))
    q = r["qos"]["runs"]
    rates = list(q.keys())
    x = np.arange(len(rates))
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.6))
    for j, (p, h) in enumerate((("fifo", "////"), ("priority", ""))):
        lat = [max(q[k][p]["CRITICAL"]["p95_ms"] or 0, 1) for k in rates]
        dr = [100 * q[k][p]["CRITICAL"]["delivery_ratio"] for k in rates]
        lab = "FIFO (no QoS)" if p == "fifo" else "priority QoS (240)"
        axes[0].bar(x + (j - 0.5) * 0.36, lat, 0.36, fc="white" if h else "0.3", ec=K, hatch=h, label=lab)
        axes[1].bar(x + (j - 0.5) * 0.36, dr, 0.36, fc="white" if h else "0.3", ec=K, hatch=h, label=lab)
    axes[0].set_yscale("log")
    axes[0].set_ylabel("critical p95 latency (ms, log)")
    axes[1].set_ylabel("critical delivery ratio (%)")
    axes[1].set_ylim(0, 110)
    for a in axes:
        a.set_xticks(x, [f"{k} B/s" for k in rates])
        a.set_xlabel("backbone capacity (offered load 1510 B/s)")
    axes[0].text(x[-1], 1.4, "0 ms\n(no queueing)", ha="center", va="bottom", fontsize=6.5)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=2, fontsize=7, frameon=False)
    fig.suptitle("FIG. 13", fontweight="bold", fontsize=11)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig13.png")

    rec = r["recovery"]
    losses = list(rec.keys())
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.6))
    styles = [("linear", "linear gap repair", "white", "...."), ("lstm", "LSTM gap repair (420)", "0.3", ""),
              ("hold", "hold-last (real time)", "white", "////"), ("forecast", "LSTM forecast (430)", "0.65", "")]
    for a, var, unit in ((axes[0], "wind", "km/h"), (axes[1], "pressure", "hPa")):
        xx = np.arange(len(losses))
        for j, (m, lab, fc, h) in enumerate(styles):
            a.bar(xx + (j - 1.5) * 0.2, [rec[l][m][var]["mae"] for l in losses], 0.2, fc=fc, ec=K, hatch=h, label=lab)
        a.set_xticks(xx, losses)
        a.set_xlabel("bursty packet-loss rate")
        a.set_ylabel(f"{var} MAE ({unit})")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=7, frameon=False)
    fig.suptitle("FIG. 14", fontweight="bold", fontsize=11)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "fig14.png")


# ---------------------------------------------------------------- FIG 15 embodiments
def fig15():
    fig, ax = canvas(8, 4.8)
    title(ax, "FIG. 15")
    items = [
        (3, "(a) Cloud-centric", ["nodes", "thin relay", "server: classify,\nQoS, reconstruct"]),
        (29, "(b) Hybrid (preferred)", ["nodes", "gateway 200:\nclassify + QoS", "server 400:\nreconstruct + fuse"]),
        (55, "(c) Edge-heavy", ["nodes + edge AI", "gateway: QoS +\nlocal alerts +\nforecast", "server:\narchive + API"]),
    ]
    for x, t, parts in items:
        ax.text(x + 11, 42, t, ha="center", fontsize=8.5, fontweight="bold")
        for k, p in enumerate(parts):
            box(ax, x, 31 - k * 10, 22, 7, p, fs=7.2)
            if k:
                arrow(ax, x + 11, 31 - (k - 1) * 10, x + 11, 38 - k * 10)
    ax.text(40, 3, "Transport variants: UDP datagrams | MQTT broker | CoAP | LoRa radio (132) with serial bridge 134",
            ha="center", fontsize=7.5)
    save(fig, "fig15.png")


# ---------------------------------------------------------------- FIG 16 packet tracer
def fig16():
    img = Image.open(os.path.join(ORIG, "packet_tracer.png")).crop((0, 0, 810, 455)).convert("L")
    img = ImageOps.autocontrast(img)
    fig = plt.figure(figsize=(8, 4.9))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.88])
    ax.imshow(img, cmap="gray")
    ax.axis("off")
    fig.suptitle("FIG. 16", fontweight="bold", fontsize=11, y=0.985)
    save(fig, "fig16.png")


if __name__ == "__main__":
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig11, fig12, fig13_14, fig15, fig16):
        f()
        print("ok", f.__name__)
