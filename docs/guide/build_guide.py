"""Builds docs/Project_Explained.pdf, a short study guide to the system and dashboard.

Run from the repository root: python docs/guide/build_guide.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
from PIL import Image as PI
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (CondPageBreak, Image, KeepTogether, ListFlowable, ListItem, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "docs", "Project_Explained.pdf")
plt.rcParams.update({"font.family": "DejaVu Sans"})

# Colours per layer
C = {"sense": "#DBEAFE", "edge": "#FDE68A", "cloud": "#D1FAE5", "shared": "#EDE9FE", "off": "#F3F4F6",
     "run": "#FCE7F3"}


# ------------------------------------------------------------------ flowchart
def flowchart(path):
    fig = plt.figure(figsize=(11, 7.6))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 76)
    ax.axis("off")

    def box(x, y, w, h, name, desc, col):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=1.2", fc=col,
                                    ec="#374151", lw=1))
        ax.text(x + w / 2, y + h - 1.6, name, ha="center", va="top", fontsize=8.6, fontweight="bold")
        ax.text(x + w / 2, y + h / 2 - 1.3, desc, ha="center", va="center", fontsize=7.1, color="#1F2937",
                linespacing=1.15)

    def group(x, y, w, h, label, col):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=2", fc=col, alpha=0.35,
                                    ec="#9CA3AF", lw=0.8, ls=(0, (4, 2))))
        ax.text(x + 1, y + h - 1, label, fontsize=8, color="#4B5563", va="top", fontstyle="italic")

    def arr(x1, y1, x2, y2, style="data", label=None, lx=0, ly=0.8, rad=0.0):
        kw = {"data": dict(lw=2.2, color="#1D4ED8", ls="-"),
              "use": dict(lw=0.9, color="#6B7280", ls="-"),
              "ctrl": dict(lw=1.3, color="#DC2626", ls=(0, (4, 2)))}[style]
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11,
                                     connectionstyle=f"arc3,rad={rad}", **kw))
        if label:
            ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, fontsize=6.6, ha="center",
                    color=kw["color"], bbox=dict(fc="white", ec="none", pad=0.6))

    ax.text(55, 74.5, "How the files connect", ha="center", va="top", fontsize=13, fontweight="bold")

    # Sensing
    group(1, 27, 25, 44, "Sensing layer", C["sense"])
    box(3, 59, 21, 8.5, "sensor_node.py", "Simulated buoy / radar:\nwind, temp, pressure", C["sense"])
    box(3, 48, 21, 8.5, "satellite_station.py", "Satellite image →\n1 KB summary (edge AI)", C["sense"])
    box(3, 37.5, 21, 8.5, "hardware/esp32_buoy", "Real ESP32 sensor\nnode over Wi-Fi", C["sense"])
    box(3, 28.5, 21, 7, "LoRa + serial_bridge.py", "Optional radio link\n→ packets", C["sense"])

    # Edge
    group(33, 36, 22, 35, "Edge gateway", C["edge"])
    box(35, 55, 18, 11, "edge_gateway.py", "Checks, classifies\n(rule + ML) and\nforwards packets", C["edge"])
    box(35, 39, 18, 10, "qos.py", "Slow link: sends\nimportant data first", C["edge"])

    # Cloud
    group(62, 33, 26, 38, "Central server", C["cloud"])
    box(64, 55, 22, 11, "central_server.py", "Fills lost packets,\ncomputes risk + forecast,\nserves API", C["cloud"])
    box(64, 44.5, 22, 7.5, "reconstruction.py", "Estimates missing\nreadings", C["cloud"])
    box(64, 35, 22, 7, "lstm.py", "Small neural network\n(numpy only)", C["cloud"])

    box(94, 55, 14.5, 11, "dashboard.html", "Live view in\nthe browser", C["cloud"])

    # Shared
    group(1, 1, 52, 23, "Shared modules (used by many files)", C["shared"])
    box(3, 13, 15, 8, "common.py", "Packet format, ports,\nthresholds (used by\nevery component)", C["shared"])
    box(20, 13, 15, 8, "ocean_model.py", "Cyclone physics +\nloss model (used by\nsensor_node.py)", C["shared"])
    box(37, 13, 14, 8, "edge_ai.py", "Image analysis + ML\n(used by gateway\n+ satellite)", C["shared"])
    box(11, 3, 32, 7.5, "run_demo.py", "Starts server, gateway, sensors and satellite together\n"
        "(mininet_topology.py does the same on an emulated WAN)", C["run"])

    # Offline
    group(58, 1, 50, 27, "Offline tools (run before / after the demo)", C["off"])
    box(60, 15, 21, 9, "train_models.py", "Trains the LSTM and\nML classifier", C["off"])
    box(85, 15, 21, 9, "models/", "Saved trained models\n(loaded by server\n+ gateway at startup)", C["off"])
    box(60, 3.5, 21, 9, "evaluate.py", "Runs experiments,\nmeasures performance", C["off"])
    box(85, 3.5, 21, 9, "results/", "REPORT.md + plots", C["off"])

    # Data flow
    arr(24, 63, 35, 61, label="UDP")
    arr(24, 52, 35, 59)
    arr(24, 41.5, 35, 57.5, label="Wi-Fi")
    arr(24, 32, 35, 56)
    arr(44, 55, 44, 49)
    arr(53, 44, 64, 58, label="priority-ordered\npackets", lx=0, ly=-1)
    arr(86, 60.5, 94, 60.5, label="WebSocket")
    # Control
    arr(70, 66, 48, 66.5, "ctrl", label="alert feedback", ly=1.4, rad=0.25)
    arr(35, 62, 24, 42, "ctrl", rad=0.2)
    ax.text(29.5, 45, "alert →\nLED /\nbuzzer", fontsize=6.4, color="#DC2626", ha="center",
            bbox=dict(fc="white", ec="#DC2626", lw=0.5, pad=1.2))
    # Uses
    arr(75, 55, 75, 52, "use")
    arr(75, 44.5, 75, 42, "use")
    arr(81, 19.5, 85, 19.5, "use", label="saves")
    arr(81, 8, 85, 8, "use", label="writes")

    # Legend
    lx, ly = 92, 30
    ax.plot([lx - 3, lx], [ly + 2, ly + 2], color="#1D4ED8", lw=2.2)
    ax.text(lx + 1, ly + 2, "data over the network", fontsize=7, va="center")
    ax.plot([lx - 3, lx], [ly, ly], color="#6B7280", lw=0.9)
    ax.text(lx + 1, ly, "uses code / files", fontsize=7, va="center")
    ax.plot([lx - 3, lx], [ly - 2, ly - 2], color="#DC2626", lw=1.3, ls=(0, (4, 2)))
    ax.text(lx + 1, ly - 2, "alert / control signal", fontsize=7, va="center")
    fig.savefig(path, dpi=200, facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------ annotated dashboard
MARKS = [(1, 1255, 30), (2, 1330, 78), (3, 11, 170), (4, 11, 300), (5, 1389, 300), (6, 11, 700), (7, 11, 960),
         (8, 1389, 960)]


def dashboard(path):
    img = PI.open(os.path.join(REPO, "docs", "dashboard.png")).crop((0, 0, 1400, 1085))
    fig = plt.figure(figsize=(10, 7.75))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(img)
    ax.axis("off")
    for n, x, y in MARKS:
        ax.add_patch(Circle((x, y), 14, fc="#F97316", ec="white", lw=2, zorder=5))
        ax.text(x, y, str(n), ha="center", va="center", color="white", fontsize=10, fontweight="bold", zorder=6)
    fig.savefig(path, dpi=170, facecolor="white")
    plt.close(fig)


# ------------------------------------------------------------------ document
FD = "/usr/share/fonts/truetype/"
pdfmetrics.registerFont(TTFont("B", FD + "liberation/LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("B-B", FD + "liberation/LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("B-I", FD + "liberation/LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("B-BI", FD + "liberation/LiberationSans-BoldItalic.ttf"))
pdfmetrics.registerFont(TTFont("SYM", FD + "dejavu/DejaVuSans.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily  # noqa: E402
registerFontFamily("B", normal="B", bold="B-B", italic="B-I", boldItalic="B-BI")

BLUE = colors.HexColor("#1E3A5F")
ACC = colors.HexColor("#F97316")
S = {
    "body": ParagraphStyle("body", fontName="B", fontSize=10, leading=14.2, alignment=TA_JUSTIFY, spaceAfter=5),
    "cell": ParagraphStyle("cell", fontName="B", fontSize=8.8, leading=11.6),
    "cellb": ParagraphStyle("cellb", fontName="B-B", fontSize=8.8, leading=11.6, textColor=colors.white),
    "h1": ParagraphStyle("h1", fontName="B-B", fontSize=16, leading=20, textColor=BLUE, spaceBefore=6, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="B-B", fontSize=12, leading=16, textColor=BLUE, spaceBefore=10, spaceAfter=4),
    "num": ParagraphStyle("num", fontName="B-B", fontSize=12, leading=16, textColor=BLUE, spaceBefore=10,
                          spaceAfter=4),
    "note": ParagraphStyle("note", fontName="B-I", fontSize=9.3, leading=13, textColor=colors.HexColor("#374151"),
                           spaceAfter=5, leftIndent=8, borderPadding=6, backColor=colors.HexColor("#FFF7ED")),
    "title": ParagraphStyle("title", fontName="B-B", fontSize=22, leading=27, textColor=BLUE, alignment=TA_CENTER),
    "sub": ParagraphStyle("sub", fontName="B", fontSize=11, leading=15, alignment=TA_CENTER,
                          textColor=colors.HexColor("#4B5563")),
}
story = []


def P(t, s="body"):
    for ch in "→⇒⇢":
        t = t.replace(ch, f'<font name="SYM">{ch}</font>')
    story.append(Paragraph(t, S[s]))


def bullets(items):
    story.append(ListFlowable([ListItem(Paragraph(i, S["body"]), leftIndent=12) for i in items],
                              bulletType="bullet", leftIndent=12, start="•"))


def numbered(items):
    story.append(ListFlowable([ListItem(Paragraph(i, S["body"]), leftIndent=16) for i in items],
                              bulletType="1", leftIndent=16, bulletFontName="B-B"))


def table(rows, widths):
    data = [[Paragraph(c, S["cellb"] if r == 0 else S["cell"]) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D1D5DB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5)]))
    story.append(t)
    story.append(Spacer(1, 6))


def section(n, title):
    story.append(CondPageBreak(45 * mm))
    story.append(Paragraph(f'<font color="#F97316">{n}</font>&nbsp;&nbsp;{title}', S["num"]))


def img(path, width_mm):
    w, h = PI.open(path).size
    story.append(Image(path, width=width_mm * mm, height=width_mm * mm * h / w))


def build():
    fc = os.path.join(HERE, "flowchart.png")
    db = os.path.join(HERE, "dashboard_annotated.png")
    flowchart(fc)
    dashboard(db)

    # ---- page 1
    P("AI-Driven Edge–Cloud Cyclone Monitoring", "title")
    story.append(Spacer(1, 3))
    P("What the system does, how the files connect, and what the dashboard shows. "
      "A 10-minute read.", "sub")
    story.append(Spacer(1, 10))
    P("1. The big picture in six steps", "h1")
    P("We are simulating a <b>cyclone monitoring network</b>. Data travels from the sea to a screen like this:")
    numbered([
        "<b>Sensors</b> (buoys and radars at sea) measure wind, temperature and pressure every second and send each "
        "reading as a small packet.",
        "A <b>satellite station</b> takes big cloud images. Instead of sending the whole 2 MB image, it analyses it "
        "on the spot and sends a ~1 KB summary, e.g. “there's a spiral storm, risk 92”.",
        "All packets go to the <b>edge gateway</b>, which sorts them by importance and sends them over a slow link "
        "to the server, <b>most important first</b>.",
        "Some packets get <b>lost</b> on the way, as real radio links lose data in bad weather. The <b>server</b> "
        "notices which ones are missing and estimates what they probably said, using a small neural network (LSTM).",
        "The server calculates a <b>cyclone risk score from 0 to 100</b>. Above 60 it declares an <b>alert</b> and "
        "tells the gateway, which tells the sensors. On real hardware an LED and buzzer switch on.",
        "The <b>dashboard</b> shows all of this live in the browser.",
    ])
    P("In the demo, a fake cyclone starts about 15 seconds in and moves towards the sensors, so you watch the "
      "system go from calm to alert and back.", "note")
    P("Three ideas to remember", "h2")
    table([["Idea", "In one sentence"],
           ["Edge AI", "Process big data (images) near where it's collected and send only the useful summary."],
           ["QoS (Quality of Service)", "When bandwidth is short, critical cyclone data goes first and unimportant "
            "data waits or is dropped."],
           ["Packet-loss recovery", "When packets go missing, estimate them with an LSTM instead of leaving gaps, "
            "and replace the estimate if the real packet arrives late."]],
          [42, 128])

    # ---- page 2: flowchart
    story.append(PageBreak())
    P("2. How the files connect", "h1")
    P("<i>Turn the page sideways to read the diagram.</i>", "sub")
    rot = os.path.join(HERE, "flowchart_rotated.png")
    PI.open(fc).rotate(90, expand=True).save(rot)
    img(rot, 158)
    story.append(PageBreak())
    P("<b>Read it left to right.</b> Data starts in the sensing layer, passes through the edge gateway, reaches "
      "the central server and ends on the dashboard. The red dashed arrows show the alert travelling back. The "
      "bottom row holds code shared by many files and the offline tools for training and testing.")
    table([["File", "What it does, in one line"],
           ["sensor_node.py", "Pretends to be a buoy/radar and sends readings; deliberately drops some packets."],
           ["satellite_station.py", "Makes satellite images, analyses them, sends only a small summary."],
           ["edge_gateway.py", "Receives everything, checks it, labels it CRITICAL / NORMAL / NON-ESSENTIAL."],
           ["qos.py", "Decides the sending order on the slow link: important data first."],
           ["central_server.py", "Detects lost packets, fills them in, computes risk, runs the website."],
           ["reconstruction.py + lstm.py", "The neural network that predicts missing readings."],
           ["edge_ai.py", "Image analysis for the satellite, plus the ML early-warning classifier."],
           ["common.py / ocean_model.py", "Shared packet format and thresholds / the fake cyclone physics."],
           ["run_demo.py", "Starts everything with one command."],
           ["train_models.py / evaluate.py", "Trains the models / measures how well everything works."]],
          [52, 118])

    # ---- page 3: dashboard
    story.append(CondPageBreak(165 * mm))
    P("3. The dashboard, piece by piece", "h1")
    P("Open http://127.0.0.1:8000 after running <font name='SYM'>python run_demo.py</font>. The numbers on the "
      "picture match the sections below.")
    img(db, 170)

    section("1", "“live (WebSocket)” (top-right)")
    P("The page is connected to the server and updates every second by itself. If it says “polling”, it is "
      "still working, just through a slightly slower method.")

    section("2", "The banner (green or red)")
    P("Example: <i>“CYCLONE ALERT ACTIVE – fused risk 91.2 (in-situ 91.2, satellite 69.9, forecast 85.0)”</i>")
    bullets([
        "<b>Green</b> = normal (risk below 60). <b>Red</b> = alert active.",
        "<b>Fused risk</b> is the final score, combining three opinions: <b>in-situ</b> (from the actual sensor "
        "readings; “in-situ” means measured on the spot), <b>satellite</b> (from the cloud images) and "
        "<b>forecast</b> (what the LSTM predicts for the next 10 readings). It is mainly the highest of the three, "
        "so any one of them can raise the alarm.",
        "The alert turns <b>on at 60</b> but only turns <b>off below 50</b>, so it doesn't flicker when the risk "
        "hovers around 60 (this is called hysteresis).",
        "<b>reconstruction: lstm</b> means lost packets are being filled in by the neural network.",
    ])

    section("3", "The seven number boxes")
    table([["Box", "Meaning"],
           ["Fused cyclone risk", "Same as the banner, 0–100."],
           ["Forecast peak risk", "The worst risk the LSTM predicts over the next 10 readings: where things are heading."],
           ["Packets received", "Total packets that reached the server."],
           ["Reconstructed (gap repair)", "Lost packets filled in <i>after</i> the next one arrived. If 10 and 13 "
            "arrived but 11 and 12 didn't, the server estimates 11 and 12."],
           ["Concealed in real time", "Guesses made <i>while still waiting</i>: if a sensor goes quiet too long, a "
            "temporary prediction is shown, then replaced when real data arrives."],
           ["Satellite bandwidth saved", "99.95% means about 1 KB was sent instead of a 2 MB image."],
           ["Critical latency p95", "Time for critical packets from gateway to server. “p95” means 95% arrived "
            "faster than this (e.g. 399 ms)."]],
          [48, 122])

    section("4", "Sensor nodes table")
    P("One row per sensor, showing its <b>latest</b> reading.")
    table([["Column", "Meaning"],
           ["Seq", "Sequence number. Every packet is numbered 1, 2, 3… A jump (10 → 13) tells the server packets were lost."],
           ["Wind / Temp / Pressure", "The reading. A cyclone means <b>high wind and low pressure</b> (normal ≈ 1010 "
            "hPa; below 990 is dangerous)."],
           ["Risk", "Risk score for this one sensor."],
           ["Class", "The gateway's label: <b>CRITICAL</b> (red) or NORMAL. “(ML 1.00)” is the ML classifier's "
            "confidence that a cyclone is coming (0 = calm, 1 = certain)."],
           ["Source", "<b>measured</b> = real packet; <b>reconstructed</b> = estimate for a lost packet; "
            "<b>forecast</b> = temporary real-time guess; <b>late packet</b> = arrived late and replaced its estimate."]],
          [42, 128])
    P("A packet can be CRITICAL while the wind is still below 60. That is the <b>ML early warning</b>: it saw "
      "the pressure dropping fast and flagged danger before the thresholds were crossed.", "note")

    section("5", "Satellite edge AI panel")
    bullets([
        "<b>Spiral picture:</b> a tiny 24×24 thumbnail of the cloud image (bright = cold, high storm clouds).",
        "<b>Risk / flag:</b> the satellite's risk score; “flag” appears at 60 or above.",
        "<b>Cold-cloud cover:</b> percentage of the image with cloud tops colder than 220 K (about −53 °C), "
        "the sign of powerful storm clouds. <b>Coldest top</b> is the coldest cloud temperature.",
        "<b>Symmetry</b> (0–1): how round and organised the storm is. <b>Eye contrast:</b> how much warmer the "
        "centre is than the ring around it; a clear warm eye means a mature cyclone.",
        "<b>Raw 2.10 MB (zlib 1.72 MB) → 1088 B sent:</b> normal compression only reaches 1.72 MB, while our edge "
        "AI sends about 1 KB. <b>Edge inference</b> is the time taken to analyse the image (≈14 ms).",
    ])

    section("6", "Telemetry history charts")
    bullets([
        "One chart per sensor, covering the last 60 readings. <b>Blue</b> = wind, <b>green</b> = pressure, "
        "<b>red dashed line</b> = 60 km/h danger threshold.",
        "<b>Yellow filled dots</b> = reconstructed values (lost packets estimated by the LSTM). "
        "<b>Hollow yellow dots</b> = temporary real-time guesses.",
        "As the cyclone arrives, blue rises above the red line and green drops; when it passes, both recover.",
        "“<b>Forecast next 10…</b>” shows the LSTM's predicted peak wind and lowest pressure coming up.",
    ])

    section("7", "Gateway QoS table: “important data first”")
    P("The heading, e.g. <i>“scheduler priority, classifier hybrid, 1200 B/s, ALERT, ML early flags 30”</i>, means: "
      "QoS is on (<b>fifo</b> would mean first come, first served); a packet is critical if the threshold rule "
      "<i>or</i> the ML says so; the link is limited to 1200 bytes/second; the gateway is in alert mode; and the "
      "ML marked 30 packets critical before the rule would have.")
    table([["Column", "Meaning"],
           ["Sent", "Packets forwarded to the server."],
           ["Queued", "Packets waiting right now."],
           ["Shed", "Unimportant packets deliberately dropped because the link was congested (only NON_ESSENTIAL)."],
           ["Dropped", "Packets lost because the queue was completely full (ideally 0)."],
           ["Avg / p95 wait", "How long packets waited at the gateway."]],
          [36, 134])
    P("Compare the rows: CRITICAL waits the least and NON_ESSENTIAL the most. That is prioritisation working.",
      "note")

    section("8", "Node health table")
    P("The NON_ESSENTIAL “housekeeping” packets each sensor sends every 5 readings: <b>Battery V</b> (battery "
      "voltage), <b>RSSI dBm</b> (radio signal strength; −60 is strong, −95 is weak) and <b>Last</b> (time of "
      "the last health packet). This is the data the gateway drops first when bandwidth is tight. If it stops "
      "updating during an alert, shedding is doing its job.")

    # ---- timeline + teacher Q&A
    story.append(CondPageBreak(90 * mm))
    P("4. What to watch during one demo run", "h1")
    table([["Time", "What happens on the dashboard"],
           ["0–15 s", "Green banner, low risk, everything NORMAL, flat lines."],
           ["~15–30 s", "Pressure starts dropping; ML confidence rises and some packets turn CRITICAL early."],
           ["~30–50 s", "Wind crosses the red line, the banner turns red, the satellite spiral brightens and shows an eye."],
           ["Whole run", "Yellow dots appear wherever packets were lost."],
           ["During alert", "In the QoS table CRITICAL stays fast while NORMAL / NON_ESSENTIAL wait longer; “Shed” may rise."],
           ["End", "The storm passes, wind falls, pressure recovers; the alert clears when risk drops below 50."]],
          [28, 142])

    story.append(CondPageBreak(75 * mm))
    P("5. Key results to quote", "h1")
    table([["What we measured", "Result"],
           ["Satellite bandwidth", "2.1 MB image → ~1 KB summary: <b>99.95% less data</b>."],
           ["Critical data on a congested link (1200 B/s)", "95% arrive within <b>0.36 s with QoS</b>, versus <b>49 s</b> without."],
           ["Very tight link (1000 B/s)", "Without QoS <b>23% of critical packets are lost</b>; with QoS, none."],
           ["ML early warning", "Flags danger about <b>16 readings before</b> the thresholds are crossed (cost: some false alarms)."],
           ["Real-time guessing of missing data", "LSTM error ~27% lower for wind and ~55% lower for pressure than repeating the last value."]],
          [62, 108])
    P("These numbers come from simulated data (results/REPORT.md). Testing on real buoy data is the next step.",
      "note")

    P("6. Questions your teacher might ask", "h1")
    for q, a in [
        ("Why UDP and not TCP?", "Marine and satellite links lose packets. TCP would keep re-sending them and "
         "add delay; with UDP we see the loss and handle it ourselves by prioritising and reconstructing."),
        ("Why process satellite images at the edge?", "Sending raw images would fill the slow link. Sending a "
         "1 KB summary leaves room for the critical sensor data."),
        ("What does the LSTM actually do?", "It learns how wind, temperature and pressure change over time. "
         "Given the last 12 readings, it predicts the next one. We use that to fill gaps and to guess overdue "
         "packets."),
        ("How is QoS different from just a priority queue?", "During an alert we keep a small reserve of "
         "bandwidth free so a critical packet never waits behind a normal one, and we drop non-essential data only "
         "when the link is actually congested, so no capacity is wasted."),
        ("What's the role of the hardware?", "An ESP32 with a pressure sensor replaces a simulated buoy. It sends "
         "the same packets, and its LED/buzzer turn on when the system declares an alert."),
    ]:
        story.append(KeepTogether([Paragraph(f"<b>Q: {q}</b>", S["body"]), Paragraph(f"A: {a}", S["body"])]))

    def deco(canv, doc):
        canv.saveState()
        canv.setFont("B", 7.5)
        canv.setFillColor(colors.HexColor("#6B7280"))
        canv.drawString(18 * mm, 10 * mm, "AI-Driven Edge–Cloud Cyclone Monitoring: study guide")
        canv.drawRightString(A4[0] - 18 * mm, 10 * mm, f"{doc.page}")
        canv.setStrokeColor(ACC)
        canv.setLineWidth(2)
        canv.line(18 * mm, A4[1] - 10 * mm, A4[0] - 18 * mm, A4[1] - 10 * mm)
        canv.restoreState()

    doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm,
                            bottomMargin=16 * mm, title="Project Explained – AI-Driven Edge–Cloud Cyclone Monitoring",
                            author="Laksh Ahuja, Anvay Sharma, Sreehari")
    doc.build(story, onFirstPage=deco, onLaterPages=deco)
    print("wrote", OUT)


if __name__ == "__main__":
    build()
