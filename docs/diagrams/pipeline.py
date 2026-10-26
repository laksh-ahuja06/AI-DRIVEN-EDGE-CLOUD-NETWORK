"""Whole-system pipeline diagram (who owns what is colour-coded).

Run from the repository root: python docs/diagrams/pipeline.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch

HERE = os.path.dirname(os.path.abspath(__file__))
K = "#1f2937"
LAKSH, ANVAY, SREE, SHARED = "#DBEAFE", "#FDE68A", "#D1FAE5", "#F3F4F6"
plt.rcParams.update({"font.family": "DejaVu Sans"})

fig = plt.figure(figsize=(16, 9.2))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 160)
ax.set_ylim(0, 92)
ax.axis("off")


def box(x, y, w, h, title, body="", fc="white", fs=8.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=1.2", fc=fc, ec=K, lw=1.1))
    ax.text(x + w / 2, y + h - 1.6, title, ha="center", va="top", fontsize=fs + 0.6, fontweight="bold")
    if body:
        ax.text(x + w / 2, y + h - 4.4, body, ha="center", va="top", fontsize=fs, linespacing=1.35)


def group(x, y, w, h, label):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=2", fc="none", ec="#6B7280",
                                lw=1.2, ls=(0, (5, 3))))
    ax.text(x + 1.5, y + h - 1.2, label, fontsize=10, fontweight="bold", color="#374151", va="top")


def arr(x1, y1, x2, y2, label="", col=K, dashed=False, lx=0, ly=1.0, fs=7.8, rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13, lw=1.4, color=col,
                                 ls=(0, (5, 3)) if dashed else "-", connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, ha="center", fontsize=fs, color=col)


ax.text(80, 90, "AI-Driven Edge–Cloud Network for Cyclone Prediction — complete pipeline", ha="center",
        fontsize=15, fontweight="bold")

# ---------------- Tier 1: sensing
group(1, 14, 35, 71, "TIER 1 · SENSING  (run_demo.py starts all)")
box(3, 63, 31, 17, "3 sensor nodes  (sensor_node.py)",
    "BUOY_07 · BUOY_12 · RADAR_COAST_A\n1 reading/s: node, seq, wind,\ntemp, pressure  (≈200 B JSON)\nstorm from ocean_model.py\n+ battery/RSSI report every 5th", SREE)
box(3, 44, 31, 15, "Satellite ground station",
    "satellite_station.py\n4-band 512×512 image = 2.1 MB\nevery 3 s", SREE)
box(3, 24, 31, 16, "Edge AI on the image  (edge_ai.py)",
    "cold cloud < 220 K, symmetry,\nwarm eye → satellite risk 0–100\n2.1 MB → ≈1 KB record\n(99.95 % less data)", ANVAY)
box(3, 15.5, 31, 6.5, "ESP32 + BMP280 node (hardware/)", "same JSON over Wi-Fi", SREE, fs=8)
arr(18.5, 44, 18.5, 40)

# radio loss
ax.add_patch(FancyBboxPatch((38.5, 60), 9, 12, boxstyle="round,pad=0.2", fc="#FEE2E2", ec="#B91C1C", lw=1))
ax.text(43, 66, "lossy radio\n≈12 % loss\nin bursts\n(Gilbert–\nElliott)", ha="center", va="center", fontsize=7.6,
        color="#7F1D1D")

# ---------------- Tier 2: edge gateway
group(50, 14, 38, 71, "TIER 2 · EDGE GATEWAY  (edge_gateway.py)")
box(52, 68, 34, 11, "① Validate", "bad JSON / out-of-range values\n→ counted and dropped", ANVAY)
box(52, 50, 34, 15, "② Classify  (rule + ML = hybrid)",
    "CRITICAL: wind ≥ 60 km/h or p ≤ 990 hPa\nor ML P(breach in 10 readings) ≥ 0.5\nor satellite risk ≥ 60\nNORMAL: the rest · NON_ESSENTIAL: battery", ANVAY)
box(52, 17, 34, 30, "③ QoS scheduler  (qos.py)",
    "token bucket on the slow link\n\nqueue 1  CRITICAL       ← sent first\nqueue 2  NORMAL\nqueue 3  NON_ESSENTIAL  ← sent last\n\nin ALERT: keep 700 B free for CRITICAL,\nshed battery reports if > 1 s backlog\nqueue full (200 pkts) → dropped", LAKSH)
arr(69, 68, 69, 65)
arr(69, 50, 69, 47)
arr(34, 72, 52, 73.5, "UDP :9001", ly=1.2)
arr(34, 32, 52, 70)
arr(34, 19, 52, 69, dashed=True)

# slow link
ax.add_patch(FancyBboxPatch((90, 27), 13, 12, boxstyle="round,pad=0.2", fc="#FEF3C7", ec="#92400E", lw=1))
ax.text(96.5, 33, "slow backbone\n1,200 B/s\n(satellite /\nmicrowave)", ha="center", va="center", fontsize=7.8,
        color="#78350F")
arr(86, 33, 90, 33)
arr(96.5, 39, 107, 73, "UDP :9002", lx=-6, ly=2, rad=-0.2)

# ---------------- Tier 3: central server
group(105, 14, 54, 71, "TIER 3 · CENTRAL SERVER  (central_server.py, FastAPI)")
box(107, 68, 24, 12, "④ Gap check", "per-node sequence numbers\nmissing / late / duplicate /\nnode restarted", LAKSH)
box(133, 68, 24, 12, "⑤ Repair  (reconstruction.py)", "LSTM (lstm.py) rebuilds lost\nreadings = yellow dots;\nlate packet → provisional\nforecast = hollow dots", SREE)
box(107, 50, 24, 14, "⑥ Node risk", "50 % wind / 60\n35 % pressure drop to 990\n15 % pressure falling\n→ 0–100", LAKSH)
box(133, 50, 24, 14, "⑦ LSTM forecast", "next 10 readings\nper node →\nforecast peak risk", ANVAY)
box(107, 29, 50, 17, "⑧ Fusion + alert",
    "fused risk = max( worst node risk,  0.9 × satellite risk,  0.8 × forecast peak )\n\nALERT ON at ≥ 60     ·     ALERT OFF below 50", LAKSH)
box(107, 15.5, 24, 11, "Dashboard  (dashboard.html)", "http://127.0.0.1:8000\nlive over WebSocket", LAKSH)
box(133, 15.5, 24, 11, "REST API", "/predict /metrics\n/telemetry /snapshot", LAKSH)
arr(131, 74, 133, 74)
arr(119, 68, 119, 64)
arr(145, 68, 145, 64)
arr(119, 50, 125, 46)
arr(145, 50, 139, 46)
arr(119, 29, 119, 26.5)
arr(145, 29, 145, 26.5)

# feedback loops
arr(107, 33, 86, 22, col="#B91C1C", dashed=True, rad=-0.25)
ax.text(96.5, 18.5, "alert feedback UDP :9003\n→ gateway switches\nto ALERT", ha="center", fontsize=7.6, color="#B91C1C")
arr(52, 30, 34, 18.5, "node alert :9004\n(buzzer / LED)", col="#B91C1C", dashed=True, lx=-2, ly=-4.5, fs=7.2)

# legend
ax.legend(handles=[Patch(fc=LAKSH, ec=K, label="Laksh"), Patch(fc=ANVAY, ec=K, label="Anvay"),
                   Patch(fc=SREE, ec=K, label="Sreehari")], loc="lower center", ncol=3, frameon=False,
          fontsize=10, bbox_to_anchor=(0.5, 0.0))
ax.text(80, 6.5, "Black arrows = data path     Red dashed = feedback / alerts     Tests: tests/test_pipeline.py (28)  ·  "
        "Offline training: train_models.py → models/  ·  Evaluation: evaluate.py → results/", ha="center", fontsize=8.5,
        color="#374151")

fig.savefig(os.path.join(HERE, "pipeline.png"), dpi=170, facecolor="white")
print("saved", os.path.join(HERE, "pipeline.png"))
