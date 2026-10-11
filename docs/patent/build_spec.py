"""Builds the Form-2 style complete specification PDF."""
import json
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (CondPageBreak, Image, KeepTogether, ListFlowable, ListItem, PageBreak,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "fig")
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, "docs", "Patent_Complete_Specification.pdf")
R = json.load(open(os.path.join(REPO, "results", "results.json")))

FD = "/usr/share/fonts/truetype/dejavu/"
LD = "/usr/share/fonts/truetype/liberation/"
pdfmetrics.registerFont(TTFont("SYM", FD + "DejaVuSans.ttf"))          # fallback for ₹ ⊙ ∧ ∈
pdfmetrics.registerFont(TTFont("DV", LD + "LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", LD + "LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-I", LD + "LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("DV-BI", LD + "LiberationSans-BoldItalic.ttf"))
pdfmetrics.registerFont(TTFont("DVM", FD + "DejaVuSansMono.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily  # noqa: E402
registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")

from reportlab.platypus import Paragraph as _Paragraph  # noqa: E402


class Paragraph(_Paragraph):
    def __init__(self, text, style=None, *a, **k):
        for ch in ("₹⊙∧∈" if isinstance(text, str) else ""):
            text = text.replace(ch, f'<font name="SYM">{ch}</font>')
        super().__init__(text, style, *a, **k)

BLUE = colors.HexColor("#2F5D8A")
LIGHT = colors.HexColor("#DCE6F2")
GREY = colors.HexColor("#7A7A7A")

TITLE = "AI-DRIVEN EDGE–CLOUD NETWORK FOR CYCLONE PREDICTION AND RESILIENT OCEAN TELEMETRY"
SHORT = "AI-Driven Edge–Cloud Cyclone Prediction & Network Resilience"
APPLICANTS = [("Laksh Ahuja", "24BDS0212"), ("Anvay Sharma", "24BCE2804"), ("Sreehari", "24BDS0417")]

ss = {
    "body": ParagraphStyle("body", fontName="DV", fontSize=9.6, leading=14, alignment=TA_JUSTIFY, spaceAfter=5),
    "small": ParagraphStyle("small", fontName="DV", fontSize=8.2, leading=11, alignment=TA_JUSTIFY, spaceAfter=3),
    "cell": ParagraphStyle("cell", fontName="DV", fontSize=7.9, leading=10.2),
    "cellb": ParagraphStyle("cellb", fontName="DV-B", fontSize=7.9, leading=10.2),
    "h1": ParagraphStyle("h1", fontName="DV-B", fontSize=15, leading=19, textColor=BLUE, spaceBefore=14, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="DV-B", fontSize=11.2, leading=15, textColor=BLUE, spaceBefore=9, spaceAfter=4),
    "center": ParagraphStyle("center", fontName="DV", fontSize=9.6, leading=13, alignment=TA_CENTER),
    "eq": ParagraphStyle("eq", fontName="DV-I", fontSize=9.8, leading=15, alignment=TA_CENTER, spaceBefore=2,
                         spaceAfter=6),
    "claim": ParagraphStyle("claim", fontName="DV", fontSize=9.4, leading=13.6, alignment=TA_JUSTIFY, spaceAfter=7,
                            leftIndent=18, firstLineIndent=-18),
    "code": ParagraphStyle("code", fontName="DVM", fontSize=7.6, leading=10, leftIndent=8, spaceAfter=1,
                           textColor=colors.HexColor("#222222")),
}

story = []
P = lambda t, s="body": story.append(Paragraph(t, ss[s]))  # noqa: E731
_h1 = [0]


def H1(t, num=True):
    story.append(CondPageBreak(60 * mm))
    if num:
        _h1[0] += 1
        t = f"{_h1[0]}.&nbsp;&nbsp;&nbsp;{t}"
    story.append(Paragraph(t, ss["h1"]))


def H2(t):
    story.append(CondPageBreak(30 * mm))
    story.append(Paragraph(t, ss["h2"]))


def bullets(items, style="body"):
    story.append(ListFlowable([ListItem(Paragraph(i, ss[style]), leftIndent=12, value="•") for i in items],
                              bulletType="bullet", start="•", leftIndent=12, bulletFontName="DV"))


def numbered(items, start=1):
    story.append(ListFlowable([ListItem(Paragraph(i, ss["body"]), leftIndent=16) for i in items],
                              bulletType="1", start=start, leftIndent=16, bulletFontName="DV-B",
                              bulletFontSize=9))


def table(rows, widths, header=True, font=None):
    data = [[Paragraph(str(c), ss["cellb"] if (header and r == 0) else ss["cell"]) for c in row]
            for r, row in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if header else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9AA5B1")),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), LIGHT))
    t.setStyle(TableStyle(st))
    story.append(t)
    story.append(Spacer(1, 6))


def eq(t):
    story.append(Paragraph(t, ss["eq"]))


def inline_fig(name, width_mm=165, caption=None):
    path = os.path.join(FIG, name)
    from PIL import Image as PI
    w, h = PI.open(path).size
    img = Image(path, width=width_mm * mm, height=width_mm * mm * h / w)
    items = [img]
    if caption:
        items.append(Paragraph(caption, ss["center"]))
    story.append(KeepTogether(items))
    story.append(Spacer(1, 6))


# =====================================================================  COVER (Form 2)
story.append(Spacer(1, 4 * mm))
P('<font name="DV-B" size="11">FORM 2</font>', "center")
P("THE PATENTS ACT, 1970 (39 of 1970)<br/>&amp;<br/>THE PATENTS RULES, 2003", "center")
story.append(Spacer(1, 3 * mm))
story.append(Paragraph("INDIAN PATENT – COMPLETE SPECIFICATION", ParagraphStyle(
    "ct", fontName="DV-B", fontSize=19, leading=24, textColor=BLUE, alignment=TA_CENTER, spaceAfter=3)))
P("(See section 10 and rule 13)<br/>Student Master Draft — Form-2 Style (Revision 2: implemented system)", "center")
story.append(Spacer(1, 7 * mm))
story.append(Paragraph(TITLE.replace(" FOR ", "<br/>FOR "), ParagraphStyle(
    "tt", fontName="DV-B", fontSize=17, leading=23, textColor=BLUE, alignment=TA_CENTER)))
story.append(Spacer(1, 5 * mm))
P("A distributed edge–cloud networking and artificial-intelligence system for bandwidth-efficient cyclone "
  "monitoring using ocean sensor nodes, satellite edge intelligence, cyclone-aware quality of service with "
  "bandwidth reservation, learned packet-loss reconstruction and a closed feedback loop to the sensing nodes",
  "center")
story.append(Spacer(1, 8 * mm))
P("<b>APPLICANTS / INVENTORS</b>", "body")
table([["Name", "Registration No.", "Nationality", "Address"]] +
      [[n, r, "[to be filled]", "[to be filled by applicant]"] for n, r in APPLICANTS],
      [45, 35, 30, 60])
P("<b>Source code and reference implementation:</b> https://github.com/laksh-ahuja06/AI-DRIVEN-EDGE-CLOUD-NETWORK",
  "small")
story.append(Spacer(1, 6 * mm))
P("<b>PREAMBLE TO THE DESCRIPTION</b>")
P("<i>The following specification particularly describes the invention and the manner in which it is to be "
  "performed.</i>")

# =====================================================================  1 TITLE
story.append(PageBreak())
H1("TITLE OF THE INVENTION")
P("AI-Driven Edge–Cloud Network for Cyclone Prediction and Resilient Ocean Telemetry")
P("<b>Alternative descriptive title:</b> A Distributed Edge–Cloud System and Method for Cyclone-Aware Traffic "
  "Prioritisation with Critical-Bandwidth Reservation, Satellite Edge Feature Extraction and Learned "
  "Reconstruction of Lost Ocean Telemetry.")

# =====================================================================  2 FIELD
H1("FIELD OF THE INVENTION")
P("The present invention relates to computer networks, distributed systems, the Internet of Things (IoT), edge "
  "computing, artificial intelligence and real-time telemetry. More particularly, it relates to a multi-tier "
  "edge–cloud system in which remote ocean and coastal sensing nodes transmit compact telemetry over lossy, "
  "bandwidth-constrained links; an edge gateway classifies and schedules that traffic according to cyclone risk; "
  "and a central prediction server reconstructs telemetry lost in transit, fuses in-situ and satellite-derived "
  "evidence into a cyclone-risk output, and feeds the resulting alert state back to the gateway and to the "
  "sensing nodes.")
P("<b>Primary application/domain:</b> cyclone monitoring and early-warning support using ocean buoys, coastal "
  "radars, satellite ground stations and a centralised prediction data centre.")

# =====================================================================  3 BACKGROUND
H1("BACKGROUND OF THE INVENTION")
P("Cyclone monitoring combines observations from geographically distributed sources: moored and drifting ocean "
  "buoys, coastal weather radars, and satellite ground stations receiving multi-spectral imagery. These sources "
  "frequently rely on low-power radio, microwave or satellite backhaul with limited capacity. Precisely when a "
  "cyclone approaches, interference and rain fade degrade those links further, producing bursty packet loss, "
  "while the operational value of the data rises sharply.")
P("A single multi-spectral satellite frame of 512 × 512 pixels in four 16-bit bands occupies about 2.1 MB; "
  "forwarding raw frames competes directly with the small but critical in-situ readings on the same backbone. "
  "Generic lossless compression does not solve this: in the inventors' measurements zlib reduced such frames by "
  "only about 17–22 %.")
P("Design target: <i>“Transmit the most important information first, predict what is missing, and keep the "
  "cyclone-monitoring network operational under constrained conditions.”</i>")
H2("Limitations of conventional or generic approaches")
bullets([
    "Raw satellite imagery consumes significant WAN/satellite bandwidth, and lossless compression recovers little of it.",
    "Static QoS policies (fixed priorities or fixed bandwidth caps) do not adapt when cyclone-related traffic "
    "suddenly becomes critical, and fixed caps waste capacity when the link is idle.",
    "Threshold-only classification raises priority only after a dangerous value has already been measured; it "
    "gives no early warning from the trend of the data.",
    "Marine and satellite links lose packets in bursts. Conventional receivers either leave gaps or repair them "
    "only after the next packet arrives, so the latest picture of the storm is missing exactly when it is needed.",
    "Retransmission-based transport (TCP) adds latency and masks rather than solves loss on intermittent links.",
    "Monitoring pipelines are typically one-directional: the field nodes are not informed when the centre "
    "declares an alert.",
])

# =====================================================================  4 PRIOR ART
H1("PRIOR ART / EXISTING TECHNOLOGIES")
P("The following is a project-level comparison against generic classes of existing systems. It is not a "
  "verified patent prior-art search; a formal search of patent and non-patent literature is required before "
  "filing (see Appendix A).")
table([
    ["Feature", "Cloud monitoring", "IoT telemetry", "Static QoS", "Present invention"],
    ["Edge processing of imagery", "Limited", "Partial", "No", "Core: ~1 KB feature record per 2.1 MB frame"],
    ["Lightweight telemetry", "Variable", "Core", "Variable", "Core: compact JSON datagrams + sequence numbers"],
    ["Cyclone-aware QoS", "No", "No", "Rule-based, fixed", "Core: strict priority + critical reserve, shedding only under congestion"],
    ["Trend-based early warning", "No", "No", "No", "Core: ML classifier flags ≈16 readings before threshold breach"],
    ["Packet-loss reconstruction", "Limited", "Limited", "No", "Core: anchored LSTM gap repair + real-time provisional forecasts"],
    ["Late-packet reconciliation", "No", "Rare", "No", "Core: estimates replaced by real data on arrival"],
    ["Feedback to field nodes", "No", "Rare", "No", "Core: server → gateway → node alert (LED/buzzer)"],
], [36, 24, 24, 26, 60])
P("<b>Technical gap identified:</b> no single networked workflow was found that combines distributed sensing, "
  "lightweight telemetry, edge feature extraction for imagery, trend-aware cyclone QoS with a work-conserving "
  "critical-bandwidth reserve, learned reconstruction of lost telemetry in both gap-repair and real-time modes, "
  "and a closed alert feedback loop to the sensing nodes.")
P("<b>Novelty statement:</b> novelty is a hypothesis, not a patentability conclusion. A prior-art search and "
  "novelty matrix are required before the claims in Section 18 are finalised.")

# =====================================================================  5 PROBLEM
H1("PROBLEM STATEMENT")
P("The technical problem addressed is how to collect, transport, process, prioritise and recover cyclone-related "
  "ocean and coastal telemetry across distributed, lossy and bandwidth-constrained networks while providing "
  "timely, explainable prediction outputs and alerts.")
H2("Technical challenges")
bullets([
    "Connect remote ocean buoys, coastal radars, satellite ground stations and low-cost hardware nodes through a "
    "multi-tier WAN/edge–cloud topology.",
    "Stream small telemetry records efficiently using MQTT/CoAP-style messaging over UDP-compatible links.",
    "Reduce backbone bandwidth by processing multi-spectral satellite imagery at the ground station.",
    "Detect cyclone-related conditions early and reserve backbone capacity for critical telemetry without wasting it.",
    "Predict or conceal missing telemetry caused by bursty packet loss, both after a gap closes and while it is open.",
    "Expose prediction results, network state and reconstruction status through REST APIs and WebSockets, and "
    "return the alert state to the field.",
])

# =====================================================================  6 OBJECTS
H1("OBJECTS OF THE INVENTION")
P("<b>Primary object:</b> to provide a distributed edge–cloud networking system that improves bandwidth "
  "efficiency, responsiveness and telemetry reliability for cyclone monitoring.")
H2("Specific objects")
bullets([
    "To provide a multi-tier network connecting buoys, coastal radars, satellite ground stations, hardware sensor "
    "nodes, an edge gateway and a central server.",
    "To provide lightweight sensor telemetry with per-node sequence numbers over constrained links.",
    "To extract compact, explainable features and a risk flag from large satellite imagery at the edge.",
    "To provide a cyclone-aware QoS scheduler that serves critical traffic first, holds a reserve of link credit "
    "for critical packets during an alert, and sheds non-essential traffic only when the link is congested.",
    "To raise traffic priority from the trend of the data before fixed thresholds are crossed.",
    "To reconstruct missing telemetry with a learned time-series model, both for closed gaps and in real time, and "
    "to reconcile late packets with their estimates.",
    "To fuse in-situ, satellite and forecast evidence into one cyclone-risk output with a hysteresis-based alert.",
    "To close the loop by feeding the alert back to the gateway and the sensing nodes.",
    "To evaluate bandwidth reduction, latency, delivery ratio, reconstruction error and early-warning lead time.",
])

# =====================================================================  7 SUMMARY
H1("SUMMARY OF THE INVENTION")
P("The invention is a distributed edge–cloud system (100) in which sensing nodes (110, 112, 114, 116) transmit "
  "compact telemetry over lossy links (130) to an edge gateway (200). The gateway validates each datagram, "
  "classifies it as CRITICAL, NORMAL or NON-ESSENTIAL using a rule classifier (222) combined with a machine-"
  "learning trend classifier (224), and transmits it over a constrained backbone (300) through a QoS scheduler "
  "(240). The scheduler serves traffic in strict priority from a token-bucket credit (244) and, during a cyclone "
  "alert, lets a non-critical packet go only if a reserve of credit (246) remains afterwards, so that a critical "
  "packet arriving next is never delayed behind it. A central prediction server (400) tracks sequence numbers, "
  "repairs gaps with an LSTM forecast anchored to the next received reading (420), publishes provisional "
  "forecasts for overdue packets in real time (430), replaces estimates with late-arriving real data (440), fuses "
  "in-situ, satellite and forecast risk (450), and sends the alert state back to the gateway (460), which "
  "relays it to the sensing nodes (260).")
P("<b>Core inventive combination:</b> distributed sensing + lightweight telemetry + satellite edge feature "
  "extraction + trend-aware cyclone QoS with a work-conserving critical-bandwidth reserve + anchored LSTM "
  "reconstruction with real-time concealment and late-packet reconciliation + closed alert feedback loop + "
  "real-time API/dashboard.")
H2("Major components/modules")
bullets([
    "<b>Edge sensing layer:</b> ocean buoys (110), coastal radars (112), satellite ground stations with edge AI "
    "(114) and microcontroller-based hardware nodes (116) measuring wind speed, temperature and pressure.",
    "<b>Transport layer:</b> compact JSON datagrams over UDP with per-node sequence numbers; MQTT, CoAP and LoRa "
    "embodiments.",
    "<b>Edge AI layer:</b> satellite feature extractor (620) and risk scorer (630) producing a ≈1 KB record; "
    "trend classifier (224) at the gateway.",
    "<b>Network intelligence layer:</b> QoS scheduler (240) with per-class queues (242), token bucket (244), "
    "critical reserve (246), congestion-gated shedding (248) and alert controller (250).",
    "<b>Prediction layer:</b> sequence tracker (410), anchored LSTM reconstructor (420), real-time concealment "
    "(430), late-packet reconciler (440), risk fusion and forecast (450).",
    "<b>Application and feedback layer:</b> REST/WebSocket API (470), dashboard (500), QoS feedback (460) and "
    "node alert notifier (260).",
])
H2("Input → processing → decision → recovery/prediction → output → feedback")
P("Sensor / imagery input → lightweight telemetry or edge feature record → gateway validation and trend-aware "
  "classification → reserve-based QoS scheduling → central reconstruction and risk fusion → REST/WebSocket "
  "output and dashboard → alert fed back to gateway and sensing nodes.")
P("<b>Key technical improvement:</b> the network does not treat every byte equally and does not wait for loss "
  "to be repaired. High-volume data is reduced at the edge, critical telemetry is protected by a reserve that "
  "costs nothing when the link is idle, priority rises on the trend of the data rather than only on thresholds, "
  "and missing values are estimated immediately and corrected as soon as better information arrives.")

# =====================================================================  8 DRAWINGS
H1("BRIEF DESCRIPTION OF THE DRAWINGS")
P("The accompanying drawings (Sheets 1–16) form part of this specification:")
table([["Figure", "Description"],
       ["FIG. 1", "Overall distributed edge–cloud system (100): sensing nodes, lossy links, edge gateway, constrained backbone, central server, dashboard and feedback paths."],
       ["FIG. 2", "Functional block diagram of the edge gateway (200)."],
       ["FIG. 3", "Functional block diagram of the central prediction server (400)."],
       ["FIG. 4", "Data structures: sensor record, gateway annotation, edge-feature record, housekeeping record, feedback and alert messages, estimate record."],
       ["FIG. 5", "Flowchart of the gateway method (steps S501–S512)."],
       ["FIG. 6", "Flowchart of the server ingest, reconstruction and concealment method (steps S601–S610)."],
       ["FIG. 7", "QoS scheduler with per-class queues, strict-priority selector, token bucket and critical reserve."],
       ["FIG. 8", "Anchored LSTM gap reconstruction compared with linear interpolation (illustrative gap near closest approach)."],
       ["FIG. 9", "Satellite edge-AI pipeline: infrared frames at increasing storm intensity and extracted features."],
       ["FIG. 10", "Sequence diagram of the alert feedback loop and gap repair."],
       ["FIG. 11", "Hardware embodiment of a sensor node (116)."],
       ["FIG. 12", "Monitoring dashboard (500) of the reference implementation during an active alert."],
       ["FIG. 13", "Measured effect of the QoS scheduler on critical latency and delivery ratio."],
       ["FIG. 14", "Measured reconstruction error for gap repair and real-time concealment."],
       ["FIG. 15", "Alternative embodiments: cloud-centric, hybrid and edge-heavy; transport variants."],
       ["FIG. 16", "Network-emulation embodiment: routed topology built in Cisco Packet Tracer."]],
      [22, 148])

# =====================================================================  9 DETAILED DESCRIPTION
H1("DETAILED DESCRIPTION OF THE INVENTION")
P("The following description refers to the drawings, in which like reference numerals denote like elements. "
  "The embodiments are illustrative; numerical values are those of the reference implementation and may be "
  "varied without departing from the invention.")

H2("9.1 Distributed edge–cloud topology (FIG. 1)")
P("The system (100) comprises a plurality of sensing nodes: ocean buoy nodes (110), coastal radar nodes (112), "
  "satellite ground stations (114) and low-cost hardware nodes (116). The nodes reach the edge gateway (200) over "
  "lossy links (130), for example marine radio, Wi-Fi or LoRa. The gateway reaches the central prediction server "
  "(400) over a constrained backbone (300), for example a 9.6–16 kbps satellite or microwave backhaul. The "
  "server serves a dashboard and API (500). Two feedback paths run in the opposite direction: QoS feedback (460) "
  "from server to gateway, and node alerts (260) from gateway to nodes.")

H2("9.2 Lightweight telemetry transport (FIG. 4)")
P("Each node sends a compact sensor telemetry record (140) as a single UDP datagram containing a node "
  "identifier, a per-node sequence number, a send timestamp, wind speed, temperature, pressure and a kind field. "
  "Example: {\"node\":\"BUOY_07\",\"seq\":1842,\"wind\":42.1,\"temp\":28.4,\"pressure\":982.6,\"kind\":\"sensor\"}. "
  "Nodes additionally send low-value housekeeping records (160) carrying battery voltage and received signal "
  "strength. The sequence number is the basis for loss detection at the server; UDP is used deliberately so that "
  "loss is exposed rather than hidden by retransmission.")
P("In a hardware embodiment (116, FIG. 11), the node converts station pressure to sea-level pressure using its "
  "configured altitude h: p<sub>0</sub> = p / (1 − h/44330)<super>5.255</super>. Without this correction an "
  "inland node at about 216 m would report about 988 hPa and be misclassified as cyclonic.")

H2("9.3 Edge AI for satellite imagery (FIG. 9)")
P("The satellite ground station (114) receives multi-band frames (in the reference implementation: visible, "
  "infrared, water-vapour and near-infrared, 16-bit). Instead of forwarding a frame, a feature extractor (620) "
  "computes from the infrared band: (a) the cold-cloud fraction, i.e. the share of pixels with brightness "
  "temperature below 220 K, indicating deep convection; (b) the coldest cloud-top temperature; (c) the storm "
  "centre as the coldness-weighted centroid; (d) an axisymmetry score from the cold-cloud cover in eight angular "
  "sectors around the centre; and (e) an eye contrast, the mean temperature of a small central disk minus that of "
  "the surrounding eyewall ring. These cues follow the logic of the Dvorak technique used by forecasters. A risk "
  "scorer (630) combines them into a 0–100 score (Section 13) and sets a risk flag at 60. A thumbnail generator "
  "(640) adds a 24 × 24 pixel infrared preview. The resulting edge-feature record (150) is about 1.0 KB and also "
  "reports the raw and transmitted byte counts so that bandwidth savings are measured continuously.")

H2("9.4 Edge gateway, validation and trend-aware classification (FIG. 2, FIG. 5)")
P("A datagram receiver (205) passes each datagram to a parse/validate module (210), which rejects records with "
  "a missing or malformed node identifier or sequence number, non-numeric measurements, or values outside "
  "physical ranges (wind 0–400 km/h, temperature −10 to 50 °C, pressure 850–1090 hPa). Rejected datagrams are "
  "counted and dropped (S503).")
P("A rule classifier (222) marks a sensor record CRITICAL when wind ≥ 60 km/h or pressure ≤ 990 hPa, marks an "
  "edge-feature record CRITICAL when its risk flag is set, and marks housekeeping records NON-ESSENTIAL. A node "
  "history buffer (230) keeps the last six readings of each node, from which seven trend features are computed: "
  "current wind and pressure, wind, pressure and temperature trend per reading, and the distance of wind and "
  "pressure to their thresholds. An ML trend classifier (224), in the reference implementation a logistic-"
  "regression model, outputs the probability that the node will breach the thresholds within the next ten "
  "readings. In the preferred hybrid policy, a class decision unit (220) marks the record CRITICAL if either the "
  "rule or the ML classifier does. The gateway appends an annotation (215) with the class, policy, ML probability "
  "and a gateway timestamp.")

H2("9.5 Cyclone-aware QoS scheduling with critical-bandwidth reserve (FIG. 7)")
P("The QoS scheduler (240) keeps one queue per class (242, 243, 245) and a token bucket (244) that accrues credit "
  "at the backbone rate r bytes/s up to a maximum B<sub>max</sub>; each packet costs its payload plus 28 bytes of "
  "UDP/IP header. A strict-priority selector (241) always considers the head of the highest-priority non-empty "
  "queue. An alert controller (250) sets the alert state when a CRITICAL packet was seen within the last ten "
  "seconds or when the server's feedback (460) reports an alert.")
P("During an alert, a NORMAL or NON-ESSENTIAL packet is transmitted only if the credit remaining after it would "
  "still be at least a reserve R (246), 700 bytes in the reference implementation; CRITICAL packets need only "
  "their own size. A critical packet arriving next therefore finds credit available immediately. Because the "
  "reserve only withholds a small fixed amount of credit, the scheduler remains work-conserving: when the link is "
  "idle, lower classes still use all spare capacity. Shedding (248) rejects NON-ESSENTIAL packets at enqueue only "
  "when an alert is active <i>and</i> more than one second's worth of traffic is already queued.")
P("The inventors first evaluated a fixed 50 % cap on NORMAL traffic during alerts and found that, below "
  "saturation, it <i>increased</i> critical latency by creating an artificial NORMAL backlog that drained in bursts. "
  "The reserve-based design of this invention removes that effect (Section 14).")

H2("9.6 Predictive packet-loss reconstruction (FIG. 3, FIG. 6, FIG. 8)")
P("A sequence tracker (410) keeps, per node, the last sequence number and an exponential moving average of the "
  "inter-arrival time. When a record arrives with a gap of n missing sequence numbers (0 &lt; n ≤ 30), the gap "
  "reconstructor (420) uses an LSTM model (700) to forecast n + 1 steps from the node's repaired history and then "
  "corrects the forecast linearly so that its last step coincides exactly with the reading just received "
  "(anchored forecast, Section 13). The n estimates are stored with the flags reconstructed = true and the "
  "method used. Longer outages are not reconstructed.")
P("<b>Real-time concealment (430).</b> A concurrent loop runs every 0.25 s. If a node's next packet is overdue by "
  "more than (2.5 + p) times its usual interval, where p is the number of provisional records already published "
  "(at most five), the module appends an LSTM forecast for the next sequence number flagged provisional = true. "
  "Interpolation is impossible at this point because no later reading exists yet. When the real packet arrives, "
  "provisional records are removed and the gap is repaired properly (S604, S606).")
P("<b>Late-packet reconciliation (440).</b> A record with an already-passed sequence number replaces a stored "
  "reconstructed estimate with the same number and is flagged late_recovered; otherwise it is discarded as a "
  "duplicate. A record with sequence number 1, or far behind the last one, is treated as a node reboot and "
  "starts a fresh stream.")
P("The LSTM (700) is implemented without external deep-learning frameworks, including backpropagation through "
  "time and the Adam optimiser, so that it runs on a small single-board computer. It takes twelve steps of six "
  "normalised inputs (levels and first differences of wind, temperature and pressure) and predicts the next "
  "differences. It is trained on 280 randomised cyclone scenarios generated by a physical model (Section 13).")

H2("9.7 Prediction, risk fusion and forecast")
P("For every record the server computes an explainable risk score from wind, pressure depression and pressure "
  "tendency. The risk fusion module (450) combines the latest in-situ risk, the latest satellite risk and the peak "
  "risk of a ten-step LSTM forecast for every node into one fused cyclone-risk output (Section 13). An alert is "
  "declared when the fused risk reaches 60 and cleared when it falls below 50 (hysteresis).")

H2("9.8 Closed feedback loop (FIG. 10)")
P("The QoS feedback transmitter (460) sends a message (465) with the alert state and fused risk to the gateway "
  "on every alert change and at least every two seconds, so the gateway can enter alert mode on evidence it "
  "cannot see itself, such as satellite risk. The gateway's node alert notifier (260) sends an alert message "
  "(265) to every node it has heard from, on each alert change and every two seconds so rebooted nodes "
  "resynchronise. In the hardware embodiment the node blinks an LED (124) and sounds a buzzer (125).")

H2("9.9 API and real-time dashboard (FIG. 12)")
P("A REST/WebSocket API (470) exposes the latest prediction and forecast, packet and recovery counters, node "
  "histories with reconstruction flags, satellite features, gateway QoS statistics and latency/bandwidth metrics. "
  "The dashboard (500) shows an alert banner (502), key indicators (504), node table (506), satellite panel "
  "(508), telemetry charts marking reconstructed and provisional points (510), per-class QoS statistics (512) "
  "and node health (514).")

H2("9.10 Hardware sensor node (FIG. 11)")
P("A hardware node (116) comprises a Wi-Fi microcontroller (118), a temperature and pressure sensor (120) on "
  "I²C, a wind sensor (121) that is either a cup anemometer with a reed or Hall switch or, for demonstration, a "
  "potentiometer, a storm-simulation button (123), an alert LED (124), a buzzer driven through a transistor (125) "
  "and optional battery/solar power (126). It sends records in the format of FIG. 4, so it can replace a "
  "simulated node without changes elsewhere. In a LoRa embodiment (132), a buoy node sends a ~30-byte CSV payload "
  "to a receiving microcontroller at the gateway, and a serial bridge (134) converts it to the standard record.")

H2("9.11 Network emulation and prototype pipeline (FIG. 16)")
P("The WAN topology was built in Cisco Packet Tracer with core, ocean, coastal and satellite routers running "
  "OSPF and end-to-end reachability verified (Appendix E). A Mininet embodiment runs the actual software "
  "components on emulated hosts with netem bandwidth, delay and loss: marine link 1 Mbps / 20 ms / 8 % loss, "
  "coastal 2 Mbps / 5 ms / 2 %, geostationary satellite 1 Mbps / 270 ms / 3 %, backbone 64 kbps / 30 ms.")

# =====================================================================  10 ARCHITECTURE
H1("SYSTEM ARCHITECTURE")
table([["Layer", "Components / operation", "Reference implementation"],
       ["Sensing / edge", "Buoys 110, radars 112, satellite ground stations 114, hardware nodes 116", "sensor_node.py, satellite_station.py, hardware/esp32_buoy"],
       ["Transport", "Compact JSON over UDP with sequence numbers; MQTT/CoAP/LoRa variants", "common.py, hardware/serial_bridge.py"],
       ["Edge AI", "Satellite feature extraction 620, risk scoring 630; trend classifier 224", "edge_ai.py"],
       ["Network intelligence", "Validation 210, hybrid classification 220, QoS scheduler 240 with reserve 246 and shedding 248", "edge_gateway.py, qos.py"],
       ["Prediction", "Sequence tracking 410, anchored LSTM 420, real-time concealment 430, late reconciliation 440, fusion 450", "central_server.py, reconstruction.py, lstm.py"],
       ["Application & feedback", "REST/WebSocket API 470, dashboard 500, QoS feedback 460, node alerts 260", "central_server.py, dashboard.html"]],
      [30, 82, 58])
H2("List of reference numerals")
nums = [("100", "Edge–cloud system"), ("110", "Ocean buoy sensor node"), ("112", "Coastal radar sensor node"),
        ("114", "Satellite ground station"), ("116", "Hardware sensor node"), ("118", "Microcontroller"),
        ("120", "Temperature/pressure sensor"), ("121", "Wind sensor"), ("122", "Sequence counter"),
        ("123", "Storm-mode button"), ("124", "Alert LED"), ("125", "Buzzer"), ("126", "Power supply"),
        ("130", "Lossy link"), ("132", "LoRa link"), ("134", "Serial bridge"), ("140", "Sensor telemetry record"),
        ("150", "Edge-feature record"), ("160", "Housekeeping record"), ("200", "Edge gateway"),
        ("205", "Datagram receiver"), ("210", "Parse/validate module"), ("215", "Gateway annotation"),
        ("220", "Class decision unit"), ("222", "Rule classifier"), ("224", "ML trend classifier"),
        ("230", "Node history buffer"), ("240", "QoS scheduler"), ("241", "Strict-priority selector"),
        ("242/243/245", "CRITICAL / NORMAL / NON-ESSENTIAL queues"), ("244", "Token bucket"),
        ("246", "Critical reserve"), ("248", "Congestion-gated shedding"), ("250", "Alert controller"),
        ("260", "Node alert notifier"), ("265", "Node alert message"), ("300", "Constrained backbone"),
        ("400", "Central prediction server"), ("405", "Datagram listener"), ("410", "Sequence tracker"),
        ("415", "Time-series store"), ("420", "Anchored gap reconstructor"), ("425", "Estimate record"),
        ("430", "Real-time concealment module"), ("440", "Late-packet reconciler"), ("450", "Risk fusion and forecast"),
        ("460", "QoS feedback transmitter"), ("465", "QoS feedback message"), ("470", "REST/WebSocket API"),
        ("500", "Dashboard (502–514 panels)"), ("620", "Feature extractor"), ("630", "Risk scorer"),
        ("640", "Thumbnail generator"), ("700", "LSTM model")]
half = (len(nums) + 1) // 2
rows = [["No.", "Element", "No.", "Element"]]
for i in range(half):
    a = nums[i]
    b = nums[i + half] if i + half < len(nums) else ("", "")
    rows.append([a[0], a[1], b[0], b[1]])
table(rows, [20, 65, 20, 65])

# =====================================================================  11 WORKING
H1("WORKING OF THE INVENTION")
H2("11.1 Operational journey")
numbered([
    "Buoys, radars and hardware nodes generate readings; satellite ground stations receive imagery.",
    "Readings are packaged as compact sequence-numbered records; ground stations replace each frame with a ≈1 KB feature record.",
    "The gateway validates each record and classifies it with the rule and trend classifiers.",
    "The gateway schedules the record on the constrained backbone, protecting critical traffic with the reserve during an alert.",
    "The server detects gaps, repairs them with the anchored LSTM, conceals overdue packets in real time and reconciles late ones.",
    "The server fuses in-situ, satellite and forecast risk and publishes prediction, network status and alerts.",
    "The alert is fed back to the gateway and, through it, to the sensing nodes.",
])
H2("11.2 End-to-end controlled pipeline")
P("Sensor stream → lightweight messaging → edge feature extraction → trend-aware classification → reserve-based "
  "QoS gateway → prediction server → anchored reconstruction / real-time concealment → risk fusion and forecast "
  "→ dashboard and alert → feedback to gateway and nodes.")

# =====================================================================  12 ALGORITHM
H1("ALGORITHM / METHOD")
P("<b>Algorithm name:</b> Adaptive Edge–Cloud Cyclone Telemetry Prioritisation and Recovery Method.")
P("<b>Input:</b> sensor telemetry, satellite frames, network state, sequence numbers and cyclone-risk indicators. "
  "<b>Output:</b> prioritised traffic, reconstructed and provisional telemetry, fused cyclone risk and forecast, "
  "network statistics and alert state delivered to the dashboard, gateway and nodes.")
H2("12.1 Gateway procedure (FIG. 5)")
for line in [
    "for each datagram d received from node a:",
    "    if not valid(d): count_invalid(); continue                 # S502-S503",
    "    w = history[a].append(d.wind, d.temp, d.pressure)            # S504",
    "    c_rule = rule(d);  p = ML(trend_features(w))                 # S505",
    "    c = CRITICAL if c_rule == CRITICAL or p >= 0.5 else c_rule",
    "    if c == CRITICAL: last_critical = now                        # S507",
    "    alert = (now - last_critical < 10 s) or server_alert",
    "    if alert and c == NON_ESSENTIAL and queued_bytes > r * 1 s: shed(d)",
    "    else: queue[c].push(d)                                       # S508",
    "loop:                                                            # S509-S510",
    "    q = highest non-empty queue;  need = size(q.head) + (R if alert and q != CRITICAL else 0)",
    "    if credit(now) >= need: send(q.pop()); credit -= size",
]:
    story.append(Paragraph(line.replace(" ", "&nbsp;"), ss["code"]))
story.append(Spacer(1, 6))
H2("12.2 Server procedure (FIG. 6)")
for line in [
    "on record x from node a with sequence s:",
    "    if s <= last[a]:",
    "        if s == 1 or last[a] - s > 50: reset(a)                 # reboot, S602",
    "        else: replace_estimate_or_discard(a, s, x); return       # S603",
    "    drop_provisional_tail(a)                                     # S604",
    "    n = s - last[a] - 1",
    "    if 0 < n <= 30:                                              # S606",
    "        f = LSTM.forecast(history[a], n + 1)",
    "        for k in 1..n: store(a, last[a]+k, f[k] + k/(n+1) * (x - f[n+1]), reconstructed)",
    "    update_interval(a); store(a, s, x); risk(x)                  # S607",
    "every 0.25 s, for each node a with p provisional records:     # S610",
    "    if now - arrival[a] > (2.5 + p) * interval[a] and p < 5:",
    "        store(a, last[a]+p+1, LSTM.forecast(history[a], p+1)[p+1], provisional)",
    "fuse risk, apply hysteresis, publish, send qos_feedback         # S608",
]:
    story.append(Paragraph(line.replace(" ", "&nbsp;"), ss["code"]))
story.append(Spacer(1, 6))
H2("Validation targets")
bullets([
    "Telemetry delivery ratio and critical-packet delivery ratio under normal and congested conditions.",
    "Backbone bytes before and after edge feature extraction, compared with raw and losslessly compressed imagery.",
    "Average and 95th-percentile latency of critical telemetry with and without QoS.",
    "Precision, recall and warning lead time of the classifiers.",
    "Reconstruction MAE/RMSE for wind, temperature and pressure under bursty loss, for gap repair and real-time concealment.",
])

# =====================================================================  13 MATHS
H1("MATHEMATICAL / TECHNICAL MODEL")
H2("13.1 Physical scenario model (training and evaluation data)")
P("A vortex approaches a node, passes and recedes; r is the node's distance from the eye, R<sub>m</sub> the "
  "radius of maximum wind, V<sub>m</sub> the maximum wind, p<sub>c</sub> the central and p<sub>e</sub> the "
  "environmental pressure.")
eq("V(r) = V<sub>m</sub> · r / R<sub>m</sub>  for r ≤ R<sub>m</sub> ;    V(r) = V<sub>m</sub> · (R<sub>m</sub> / r)<super>0.6</super>  for r &gt; R<sub>m</sub>     (modified Rankine)")
eq("p(r) = p<sub>c</sub> + (p<sub>e</sub> − p<sub>c</sub>) · exp[ −(R<sub>m</sub> / r)<super>B</super> ],   B = 1.5     (Holland)")
P("AR(1) gusts, a diurnal temperature cycle and rain cooling are added. Packet loss follows a two-state "
  "Gilbert–Elliott channel with good- and bad-state loss probabilities and transition probabilities chosen to "
  "give the target mean loss and burst length.")
H2("13.2 Classification")
eq("c<sub>rule</sub> = CRITICAL  if  wind ≥ 60 km/h  or  p ≤ 990 hPa")
eq("P(breach within H = 10 readings | z) = σ(w · ẑ + b),    ẑ = (z − μ) / s,    σ(u) = 1 / (1 + e<super>−u</super>)")
P("where z holds the seven trend features of Section 9.4, trained by class-weighted gradient descent on "
  "labels generated from the scenario model.")
H2("13.3 QoS scheduling with critical reserve")
eq("B(t) = min( B<sub>max</sub> , B(t<sub>0</sub>) + r · (t − t<sub>0</sub>) )")
eq("transmit head packet q  iff  B(t) ≥ size(q) + R · 1[ alert ∧ class(q) ≠ CRITICAL ]")
eq("shed NON-ESSENTIAL at enqueue  iff  alert ∧ Q<sub>bytes</sub> &gt; r · τ<sub>shed</sub>,    τ<sub>shed</sub> = 1 s")
H2("13.4 LSTM cell and anchored reconstruction")
eq("[i, f, o, g] = [σ, σ, σ, tanh]( W [x<sub>t</sub>, h<sub>t−1</sub>] + b ),   c<sub>t</sub> = f ⊙ c<sub>t−1</sub> + i ⊙ g,   h<sub>t</sub> = o ⊙ tanh(c<sub>t</sub>)")
P("Given the history up to the last received reading and the reading x<sub>n+1</sub> received after a gap of n, "
  "the LSTM produces forecasts f<sub>1</sub> … f<sub>n+1</sub>; the stored estimates are:")
eq("x<sub>k</sub>* = f<sub>k</sub> + (k / (n + 1)) · ( x<sub>n+1</sub> − f<sub>n+1</sub> ),    k = 1 … n")
P("so the estimates follow the learned dynamics and join the received reading without a discontinuity. In real "
  "time, before x<sub>n+1</sub> exists, the provisional estimate is f<sub>k</sub> itself.")
H2("13.5 Risk scoring and fusion")
eq("risk = 100 · [ 0.5 · min(1, wind/60) + 0.35 · clip((1013 − p)/23, 0, 1) + 0.15 · clip(−Δp, 0, 1) ]")
eq("sat_risk = 40 · cover · depth + 30 · symmetry · cover + 30 · eye")
P("with cover = min(1, cold_frac/0.06), depth = clip((220 − min_bt)/25, 0, 1) and eye = clip(eye_contrast/40, 0, 1).")
eq("R<sub>fused</sub> = max( R<sub>in-situ</sub> , 0.9 · R<sub>sat</sub> , 0.8 · R<sub>forecast</sub> );   alert on at 60, off below 50")
H2("Performance metrics")
bullets(["Bandwidth reduction percentage versus raw and versus zlib-compressed imagery.",
         "Packet delivery ratio and critical-packet delivery ratio.", "Average and p95 latency of critical telemetry.",
         "Precision, recall, F1 and mean warning lead time.", "MAE/RMSE of reconstructed telemetry.",
         "Dashboard update latency and end-to-end availability."])

# =====================================================================  14 EXAMPLES
H1("EXAMPLES / WORKING EMBODIMENTS")
P("The reference implementation (Python 3, FastAPI, numpy; 28 automated tests) was evaluated on held-out "
  "simulated scenarios not used for training. The figures below measure the mechanisms on synthetic data; "
  "validation on archived buoy data is future work (Section 16).")
P("<b>Example 1 — normal ocean monitoring.</b> Wind, temperature and pressure records stream through the "
  "gateway; all traffic is NORMAL, the fused risk stays low and no alert is raised.")
P("<b>Example 2 — cyclone threshold detected, with early warning.</b> As a storm approaches, the ML trend "
  "classifier flags falling pressure and rising wind before the thresholds are crossed; the gateway enters alert "
  "mode, holds the critical reserve and, under congestion, sheds housekeeping traffic.")
c = R["classifier"]
table([["Policy", "Precision", "Recall", "F1", "Mean warning lead (readings)", "Calm scenarios with false alarm"]] +
      [[m, c[m]["precision"], c[m]["recall"], c[m]["f1"], c[m]["mean_lead_readings"],
        f'{c[m]["calm_traces_with_false_alarm"]} of {c["calm_traces"]}'] for m in ("rule", "ml", "hybrid")],
      [22, 22, 20, 18, 45, 43])
P("<b>Example 3 — constrained backbone.</b> Four buoys, a satellite station and housekeeping traffic offered "
  f"{R['qos']['offered_load_bps']:.0f} B/s to backbones of different capacity, using the same scheduler code as "
  "the live gateway driven by a simulated clock (FIG. 13).")
rows = [["Backbone", "Scheduler", "Critical delivered", "Critical avg / p95 latency", "Normal delivered",
         "Non-essential delivered"]]
for rate, runs in R["qos"]["runs"].items():
    for p_, r_ in runs.items():
        cr, nr, ne = r_["CRITICAL"], r_["NORMAL"], r_["NON_ESSENTIAL"]
        rows.append([f"{rate} B/s", "FIFO (no QoS)" if p_ == "fifo" else "Invention",
                     f"{100 * cr['delivery_ratio']:.1f} %", f"{cr['avg_ms']:.0f} / {cr['p95_ms']:.0f} ms",
                     f"{100 * nr['delivery_ratio']:.1f} %", f"{100 * ne['delivery_ratio']:.1f} %"])
table(rows, [22, 28, 28, 38, 26, 28])
P("At 1200 B/s the critical p95 latency fell from about 49 s to 356 ms; at 1000 B/s FIFO delivered only 77 % of "
  "critical packets against 100 %. With spare capacity (2000 B/s) both schedulers behave identically and nothing "
  "is shed, confirming that the reserve and shedding cost nothing when the link is idle.")
P("<b>Example 4 — packet loss and recovery.</b> Bursty loss at 5–20 % (FIG. 14). For real-time concealment the "
  "LSTM forecast lowered error versus holding the last value by about 27 % for wind and 53–57 % for pressure. "
  "For gap repair the anchored LSTM lowered pressure error by 7–15 % and temperature error by about 6 % versus "
  "linear interpolation, and was equivalent for wind, whose gust component is essentially unpredictable.")
rec = R["recovery"]
rows = [["Loss", "Variable", "Linear gap repair", "Anchored LSTM", "Hold-last (real time)", "LSTM forecast (real time)"]]
for loss, rr in rec.items():
    for v in ("wind", "temp", "pressure"):
        rows.append([loss, v, rr["linear"][v]["mae"], rr["lstm"][v]["mae"], rr["hold"][v]["mae"], rr["forecast"][v]["mae"]])
table(rows, [16, 22, 32, 30, 34, 36])
P("<b>Example 5 — edge processing of satellite imagery.</b> A ground station receives 4-band 16-bit frames; the "
  "feature extractor sends only the feature record (FIG. 9).")
rows = [["Frame", "Raw", "zlib", "Sent", "Saved vs raw", "Saved vs zlib", "Edge risk", "Inference"]]
for b in R["bandwidth"]:
    if b["intensity"] in (0.0, 1.0):
        rows.append([f'{b["size"]}², I={b["intensity"]}', f'{b["raw_bytes"] / 1e6:.2f} MB', f'{b["zlib_bytes"] / 1e6:.2f} MB',
                     f'{b["feature_bytes"]} B', f'{b["reduction_pct"]} %', f'{b["reduction_vs_zlib_pct"]} %',
                     b["sat_risk"], f'{b["inference_ms"]} ms'])
table(rows, [26, 18, 18, 16, 24, 24, 18, 20])
P("<b>Example 6 — closed loop with hardware.</b> A microcontroller node with a pressure sensor and a wind input "
  "sends records to the gateway; when the operator raises the wind input or activates storm mode, the records "
  "become CRITICAL, the fused risk crosses 60, and the alert returns to the node, which activates its LED and "
  "buzzer (FIG. 10, FIG. 11). Physically induced loss, for example by shielding the node, appears as reconstructed "
  "points on the dashboard (FIG. 12). <i>The firmware has been written and syntax-checked; the physical build is "
  "planned for the next review.</i>")
P("<b>Example 7 — live end-to-end run.</b> In an 85-second run with three simulated nodes, a satellite station, "
  "12 % bursty loss and a 1200 B/s backbone, the dashboard reported 275 packets, 27 gap reconstructions, 6 "
  "real-time concealments, 99.95 % satellite bandwidth saving and a gateway-to-server critical p95 latency of "
  "about 0.4 s (FIG. 12).")

# =====================================================================  15 ALTERNATIVES
H1("ALTERNATIVE EMBODIMENTS")
bullets([
    "Cloud-centric embodiment with classification and scheduling at the central data centre (FIG. 15a).",
    "Hybrid embodiment with gateway classification/QoS and central reconstruction and fusion (FIG. 15b, preferred).",
    "Edge-heavy embodiment in which the gateway also forecasts and raises local alerts (FIG. 15c).",
    "MQTT-based embodiment using a broker between nodes and gateway; CoAP-based constrained-device embodiment.",
    "LoRa embodiment with compact CSV payloads and a serial bridge (132, 134).",
    "Single-board-computer gateway (e.g. Raspberry Pi) separate from the central server.",
    "Rule-only, ML-only or hybrid classification; logistic regression replaced by another classifier or a "
    "reinforcement-learning policy.",
    "LSTM replaced by a GRU, temporal convolutional network or other sequence model; linear interpolation as fallback.",
    "Different reserve sizes, alert hold times, shedding thresholds or fusion weights.",
    "Real satellite products (e.g. infrared imagery from operational geostationary satellites) instead of synthetic frames.",
    "REST-only or REST + WebSocket dashboard; Mininet or Cisco Packet Tracer network emulation.",
])

# =====================================================================  16 ADVANTAGES
H1("TECHNICAL ADVANTAGES")
bullets([
    "Reduces backbone bandwidth for imagery by about 99.95 % at 512 × 512 pixels, far beyond lossless compression.",
    "Keeps critical latency in the sub-second range under congestion where FIFO queues reach tens of seconds.",
    "Protects critical traffic with a reserve that wastes no capacity when the link is idle.",
    "Raises priority on the trend of the data, on average about 16 readings before thresholds are crossed.",
    "Publishes estimates of missing telemetry immediately and replaces them with better estimates or real data as "
    "soon as either is available.",
    "Closes the loop to the field: nodes learn the alert state and can warn locally.",
    "Runs on low-cost hardware: the learned models need only numpy; nodes cost about ₹800 each.",
    "Separates transport, edge AI, QoS, prediction and dashboard so each can be replaced independently.",
])
P("<b>Known limitations:</b> results are from simulated scenarios; the ML classifier trades precision (0.72) for "
  "recall and raised false alarms on 3 of 9 calm scenarios; LSTM gap repair offers no gain for wind; the "
  "hardware build and the Mininet embodiment are yet to be exercised physically.", "small")

# =====================================================================  17 INDUSTRIAL
H1("INDUSTRIAL APPLICABILITY")
P("The invention is applicable to distributed environmental-monitoring and disaster-management systems in which "
  "remote sensing nodes communicate across bandwidth-constrained or intermittently connected networks.")
H2("Potential application areas")
bullets(["Cyclone and severe-weather monitoring networks.", "Oceanographic and coastal sensor networks.",
         "Satellite ground-station telemetry systems.", "Disaster-resilient IoT communication infrastructure.",
         "Flood, storm-surge and landslide early-warning networks.",
         "Remote sensing systems requiring bandwidth-aware data reduction.",
         "Real-time network monitoring and adaptive QoS research platforms."])
P("Deployment environment: distributed sensor nodes, edge gateways, satellite-ground-station processing nodes, a "
  "central prediction server and a web dashboard. Coastal and island communities, which often have the weakest "
  "connectivity, benefit from a network that degrades gracefully instead of failing silently.")

# =====================================================================  18 CLAIMS
H1("CLAIMS")
P("We claim:")
claims = [
    "A distributed edge–cloud telemetry system (100) for cyclone monitoring, comprising: a plurality of sensing "
    "nodes (110, 112, 114, 116), each configured to transmit telemetry records (140) carrying a node identifier and "
    "a per-node sequence number over a lossy link (130); an edge gateway (200) comprising a validation module (210), "
    "a traffic classifier (220) configured to assign each record to one of a critical, a normal and a non-essential "
    "class, and a QoS scheduler (240) configured to transmit the records over a constrained backbone link (300) "
    "from per-class queues (242, 243, 245) in strict priority subject to a token-bucket credit (244); and a central "
    "prediction server (400) comprising a sequence tracker (410) and a reconstructor (420) configured to estimate "
    "records missing from a node's sequence; <b>characterised in that</b> the QoS scheduler (240), while an alert "
    "state is active, transmits a record of the normal or non-essential class only if the token-bucket credit "
    "remaining after its transmission is at least a predetermined reserve (246), and transmits a record of the "
    "critical class whenever the credit covers its own size, and in that the central prediction server (400) "
    "transmits a feedback message (465) indicating a cyclone-alert state to the edge gateway (200), which sets "
    "the alert state in response.",
    "The system as claimed in claim 1, wherein the QoS scheduler (240) rejects a record of the non-essential "
    "class at enqueue only when the alert state is active and the bytes already queued exceed the backbone rate "
    "multiplied by a predetermined time, such that non-essential records are delivered when the link has spare "
    "capacity.",
    "The system as claimed in claim 1, wherein the traffic classifier (220) comprises a rule classifier (222) "
    "applying wind-speed and pressure thresholds and a machine-learning classifier (224) operating on trend "
    "features computed from a buffer (230) of the node's recent readings and trained to predict a threshold breach "
    "within a future horizon, and assigns the critical class when either classifier indicates criticality.",
    "The system as claimed in claim 3, wherein the trend features comprise the current wind speed and pressure, "
    "the per-reading trends of wind speed, pressure and temperature, and the distances of wind speed and pressure "
    "from their respective thresholds.",
    "The system as claimed in claim 1, wherein, upon receiving a record after a gap of n missing sequence "
    "numbers, the reconstructor (420) obtains from a recurrent neural network (700) forecasts f<sub>1</sub> … "
    "f<sub>n+1</sub> from the node's history and stores, for k = 1 … n, the estimate f<sub>k</sub> + (k/(n+1))·"
    "(x<sub>n+1</sub> − f<sub>n+1</sub>), where x<sub>n+1</sub> is the received record, each estimate being "
    "flagged as reconstructed.",
    "The system as claimed in claim 1, wherein the central prediction server (400) further comprises a real-time "
    "concealment module (430) configured to determine that a node's next record is overdue relative to an average "
    "inter-arrival interval of that node, to store a forecast for the next sequence number flagged as provisional, "
    "and to remove provisional records when a record of that node is subsequently received.",
    "The system as claimed in claim 1, wherein the central prediction server (400) further comprises a late-packet "
    "reconciler (440) configured to replace a stored reconstructed estimate with a subsequently received record "
    "bearing the same sequence number, and to treat a record bearing sequence number one, or a sequence number "
    "lower than the last by more than a predetermined margin, as the start of a new stream of a rebooted node.",
    "The system as claimed in claim 1, wherein at least one sensing node is a satellite ground station (114) "
    "comprising a feature extractor (620) configured to compute, from an infrared band of a multi-spectral frame, "
    "a cold-cloud fraction, a coldest cloud-top temperature, a storm centre, an axisymmetry score over angular "
    "sectors and an eye contrast, and a risk scorer (630) configured to derive a risk value and risk flag "
    "therefrom, the ground station transmitting an edge-feature record (150) containing said features in place of "
    "the frame.",
    "The system as claimed in claim 8, wherein the central prediction server (400) comprises a risk-fusion module "
    "(450) computing a fused risk as the maximum of an in-situ risk, a weighted satellite risk and a weighted peak "
    "of forecast risk, and sets and clears the cyclone-alert state at different thresholds.",
    "The system as claimed in claim 1, wherein the edge gateway (200) further comprises a node alert notifier "
    "(260) configured to transmit the alert state to each sensing node from which a record has been received, on "
    "every change of the alert state and periodically, and wherein at least one sensing node (116) comprises an "
    "alert indicator (124, 125) activated in response.",
    "The system as claimed in claim 10, wherein the sensing node (116) comprises a microcontroller (118), a "
    "pressure sensor (120) and a wind sensor (121), and converts measured station pressure to sea-level pressure "
    "using a configured altitude before transmission.",
    "The system as claimed in claim 1, wherein the recurrent neural network (700) is a long short-term memory "
    "network trained on scenarios generated from a cyclone wind and pressure profile model and a two-state bursty "
    "loss channel model.",
    "A method for cyclone-aware telemetry prioritisation and recovery, comprising the steps of: (a) receiving, at "
    "an edge gateway, sequence-numbered telemetry records from sensing nodes over lossy links (S501); (b) "
    "validating each record (S502); (c) classifying each record as critical, normal or non-essential using a "
    "threshold rule and a trend-based machine-learning classifier (S505); (d) setting an alert state when a "
    "critical record has been received within a hold time or when a server reports an alert (S507); (e) queuing "
    "each record by class (S508); (f) transmitting queued records over a constrained backbone in strict priority "
    "from a token-bucket credit, wherein during the alert state a non-critical record is transmitted only if a "
    "reserve of credit remains after its transmission (S509, S510); (g) at a central server, detecting missing "
    "sequence numbers and storing anchored forecast estimates for them (S606); (h) computing a fused cyclone risk "
    "(S608); and (i) transmitting the resulting alert state back to the edge gateway.",
    "The method as claimed in claim 13, further comprising storing a provisional forecast for a node whose next "
    "record is overdue and replacing it when that node's next record is received (S604, S610).",
    "The method as claimed in claim 13, further comprising replacing a stored estimate with a late-arriving "
    "record bearing the same sequence number.",
    "The method as claimed in claim 13, further comprising, at a satellite ground station, extracting from a "
    "multi-spectral frame a feature record of cold-cloud fraction, coldest cloud top, storm centre, axisymmetry "
    "and eye contrast together with a risk flag, and transmitting the feature record in place of the frame.",
    "The method as claimed in claim 13, further comprising shedding non-essential records at the edge gateway "
    "only while the alert state is active and the queued backlog exceeds a predetermined amount.",
    "The method as claimed in claim 13, further comprising relaying the alert state from the edge gateway to the "
    "sensing nodes and activating an alert indicator at a sensing node.",
    "A non-transitory computer-readable medium storing instructions which, when executed by one or more "
    "processors of an edge gateway and a central server, cause them to perform the method as claimed in any one "
    "of claims 13 to 18.",
]
for i, c_ in enumerate(claims, 1):
    story.append(Paragraph(f"<b>{i}.</b>&nbsp;&nbsp;{c_}", ss["claim"]))
story.append(Spacer(1, 8 * mm))
P("Dated this ____ day of ______________, 2026")
story.append(Spacer(1, 10 * mm))
table([["", "", ""], [f"{n}<br/>({r})" for n, r in APPLICANTS]], [56, 56, 56], header=False)
P("Signatures of the Applicants", "center")

# =====================================================================  19 ABSTRACT
story.append(PageBreak())
H1("ABSTRACT")
P("<b>AI-Driven Edge–Cloud Network for Cyclone Prediction and Resilient Ocean Telemetry</b>", "center")
story.append(Spacer(1, 3 * mm))
P("A distributed edge–cloud system (100) for cyclone monitoring is disclosed. Ocean buoys, coastal radars, "
  "hardware nodes and satellite ground stations (110–116) send compact, sequence-numbered telemetry over lossy "
  "links; ground stations replace multi-megabyte frames with ≈1 KB edge-feature records. An edge gateway (200) "
  "validates records, classifies them using a threshold rule and a trend-based machine-learning classifier, and "
  "schedules them over a constrained backbone in strict priority; during a cyclone alert, non-critical records "
  "are sent only if a reserve of link credit remains, and non-essential records are shed only under congestion. "
  "A central server (400) reconstructs missing records with an LSTM forecast anchored to the next received "
  "reading, publishes provisional forecasts for overdue records, reconciles late records, fuses in-situ, "
  "satellite and forecast risk, and returns the alert state to the gateway, which relays it to the nodes. "
  "(FIG. 1)")
P("Word count of abstract body: under 150 words.", "small")

# =====================================================================  DRAWINGS
DRAW = [f"fig{n:02d}.png" for n in range(1, 17)]
for k, name in enumerate(DRAW, 1):
    story.append(PageBreak())
    hdr = Table([[Paragraph(f"Applicants: {', '.join(n for n, _ in APPLICANTS)}", ss["cell"]),
                  Paragraph(f"Total sheets: 16<br/>Sheet {k} of 16", ParagraphStyle("r", parent=ss["cell"], alignment=2))]],
                colWidths=[120 * mm, 50 * mm])
    story.append(hdr)
    story.append(Spacer(1, 6 * mm))
    from PIL import Image as PI
    w, h = PI.open(os.path.join(FIG, name)).size
    W = 168 * mm
    H = W * h / w
    if H > 205 * mm:
        H = 205 * mm
        W = H * w / h
    story.append(Image(os.path.join(FIG, name), width=W, height=H))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Signatures of the Applicants: ____________________", ParagraphStyle(
        "sig", parent=ss["cell"], alignment=2)))

# =====================================================================  APPENDICES
story.append(PageBreak())
H1("APPENDIX A — TECHNICAL GAP &amp; NOVELTY HYPOTHESIS", num=False)
P("This table is a project-level hypothesis and must not be treated as a verified patent novelty matrix.")
table([["Feature", "Cloud", "IoT telemetry", "Static QoS", "Proposed"],
       ["Edge processing", "Limited", "Partial", "Limited", "Core"],
       ["Lightweight transport", "Variable", "Core", "Variable", "Core"],
       ["AI-driven, trend-aware QoS", "No", "No", "Rule-based", "Core"],
       ["Work-conserving critical reserve", "No", "No", "Fixed caps", "Core"],
       ["Packet-loss prediction (gap + real time)", "Limited", "Limited", "No", "Core"],
       ["Late-packet reconciliation", "No", "Rare", "No", "Core"],
       ["Feedback loop to field nodes", "No", "Rare", "No", "Core"],
       ["Cyclone-aware priority", "Manual/fixed", "Partial", "Fixed", "Core"]],
      [56, 26, 28, 28, 32])
P("<b>Before filing:</b> search patent databases (InPASS, Google Patents, Espacenet, WIPO PATENTSCOPE) and "
  "non-patent literature for: QoS with priority reservation for disaster telemetry; edge satellite-image feature "
  "extraction; LSTM imputation of sensor data; feedback-driven alerting in IoT networks. Revise claim 1's "
  "characterising portion to whatever combination survives that search, preferably with a registered patent agent.",
  "small")

H1("APPENDIX B — FROM MVP TO IMPLEMENTED SYSTEM", num=False)
table([["MVP element (Review 1 plan)", "Review 1 status", "Implemented (this revision)"],
       ["Network", "Packet Tracer topology, OSPF, ping verified", "Unchanged + Mininet embodiment with netem link impairments"],
       ["Telemetry", "UDP JSON, random loss", "Physics-based cyclone model, bursty Gilbert–Elliott loss, housekeeping traffic, validation"],
       ["Edge AI", "Not started", "Satellite ground station: 4-band frames → ≈1 KB features, risk flag, thumbnail"],
       ["QoS", "Threshold rule + 0.5 s sleep", "Token-bucket scheduler, 3 classes, critical reserve, congestion-gated shedding, ML + hybrid classifier"],
       ["Prediction", "Linear interpolation", "Anchored numpy LSTM, real-time concealment, late reconciliation, risk fusion, 10-step forecast"],
       ["Dashboard", "Polling HTML table", "WebSocket dashboard with charts, satellite panel, QoS and node-health tables"],
       ["Feedback", "None", "Server → gateway QoS feedback; gateway → node alerts"],
       ["Hardware", "None", "ESP32 + BMP280 node firmware, LoRa option, serial bridge"],
       ["Evaluation", "12 s smoke test", "Reproducible evaluation (Section 14), 28 automated tests"]],
      [42, 50, 78])

H1("APPENDIX C — EVALUATION PLAN", num=False)
table([["Area", "Measures", "Test basis", "Status"],
       ["Bandwidth", "Bytes; reduction %", "Raw vs zlib vs edge features", "Done (Example 5)"],
       ["QoS", "Critical delivery; avg/p95 latency", "FIFO vs invention at 4 capacities", "Done (Example 3)"],
       ["Classifier", "Precision, recall, lead time", "Held-out scenarios", "Done (Example 2)"],
       ["Recovery", "MAE/RMSE", "Bursty loss 5/10/20 %", "Done (Example 4)"],
       ["System", "Throughput; API/WebSocket latency", "End-to-end scripted run", "Done (Example 7)"],
       ["Field data", "All of the above", "Archived buoy data (e.g. INCOIS, NOAA NDBC)", "Planned"],
       ["Hardware", "Delivery, alert round trip", "ESP32 nodes on Wi-Fi/LoRa", "Planned"]],
      [24, 46, 58, 42])
P("Success definition: reduce unnecessary backbone traffic, protect critical telemetry during increased cyclone "
  "risk, recover useful information from packet loss, and deliver prediction results with measurable latency and "
  "reliability.")

H1("APPENDIX D — HARDWARE EMBODIMENT (COLLEGE-SCALE)", num=False)
table([["Item", "Qty", "Approx. ₹ each", "Role"],
       ["ESP32 DevKit V1", "2", "350–450", "Microcontroller 118 with Wi-Fi"],
       ["BMP280 (or BME280)", "2", "100–150", "Temperature/pressure sensor 120"],
       ["10 kΩ potentiometer / reed-switch anemometer", "2", "10–40", "Wind sensor 121"],
       ["Active buzzer + BC547 + 1 kΩ", "2", "20–30", "Buzzer 125"],
       ["Breadboard, jumpers, USB cables", "—", "300–400", "Assembly"],
       ["Optional: 2× SX1278 LoRa + antennas", "—", "800–1,100", "LoRa link 132"],
       ["Optional: Raspberry Pi", "1", "lab", "Separate edge gateway 200"]],
      [62, 14, 30, 64])
P("Wiring: BMP280 to 3.3 V, GND, SCL GPIO22, SDA GPIO21; potentiometer wiper to GPIO34 or reed switch to GPIO27; "
  "buzzer through the transistor from GPIO25; on-board LED GPIO2; BOOT button GPIO0 toggles storm mode. Full "
  "guide: hardware/README.md in the repository.")

H1("APPENDIX E — NETWORK EMULATION IN CISCO PACKET TRACER", num=False)
P("The routed WAN of the invention was implemented in Cisco Packet Tracer (FIG. 16): a core router connected by "
  "WAN links to ocean, coastal and satellite routers, each serving a switch with the corresponding end devices, "
  "and a data-centre switch with prediction server, dashboard server and network-admin PC. OSPF area 0 provides "
  "routing; a successful ping from BUOY-01 to the prediction server verified the end-to-end path.")
table([["Network", "Subnet", "Purpose"], ["Ocean buoys", "10.10.10.0/24", "Buoy telemetry"],
       ["Coastal radar", "10.20.20.0/24", "Radar data"], ["Satellite ground", "10.30.30.0/24", "Satellite data"],
       ["Data centre", "10.40.40.0/24", "Servers"], ["Ocean–core WAN", "10.100.1.0/30", "WAN"],
       ["Coast–core WAN", "10.100.2.0/30", "WAN"], ["Satellite–core WAN", "10.100.3.0/30", "WAN (serial)"]],
      [50, 50, 70])
table([["Device", "IP address", "Gateway"], ["BUOY-01 / 02 / 03", "10.10.10.11 / .12 / .13", "10.10.10.1"],
       ["RADAR-01 / 02", "10.20.20.11 / .12", "10.20.20.1"], ["SAT-GS-01 / 02", "10.30.30.11 / .12", "10.30.30.1"],
       ["PREDICTION-SERVER", "10.40.40.10", "10.40.40.1"], ["DASHBOARD-SERVER", "10.40.40.20", "10.40.40.1"],
       ["NETWORK-ADMIN", "10.40.40.30", "10.40.40.1"]], [50, 60, 60])
P("Representative router configuration (R-OCEAN); R-COAST, R-SAT and R-CORE follow the same pattern with their "
  "subnets:", "small")
for line in ["enable", "configure terminal", "hostname R-OCEAN", "interface gigabitEthernet 0/0",
             " ip address 10.10.10.1 255.255.255.0", " no shutdown", "interface gigabitEthernet 0/1",
             " ip address 10.100.1.1 255.255.255.252", " no shutdown", "router ospf 1",
             " network 10.10.10.0 0.0.0.255 area 0", " network 10.100.1.0 0.0.0.3 area 0", "end", "write memory"]:
    story.append(Paragraph(line.replace(" ", "&nbsp;"), ss["code"]))
story.append(Spacer(1, 4))
P("Verification: <font name='DVM'>ping 10.40.40.10</font> from BUOY-01; <font name='DVM'>show ip route</font>, "
  "<font name='DVM'>show ip ospf neighbor</font>, <font name='DVM'>show ip interface brief</font> on the routers.",
  "small")

H1("APPENDIX F — DEVELOPMENT RECORD", num=False)
H2("Problems encountered and how the team adapted")
bullets([
    "<b>Race condition on startup (Review 1):</b> the server's UDP listener was not running before sensors started; "
    "fixed by starting it from the application's startup/lifespan hook.",
    "<b>Background process isolation (Review 1):</b> separately launched processes lost their working directory; "
    "replaced by a single launcher (run_demo.py) that starts all components in one process group.",
    "<b>Reconstruction only after the gap closes (Review 1):</b> addressed in this revision by real-time "
    "provisional forecasts (430), later replaced by gap repair.",
    "<b>Fixed bandwidth cap hurt critical latency:</b> a 50 % cap on NORMAL traffic during alerts created bursts "
    "that delayed critical packets below saturation; replaced by the work-conserving reserve (246).",
    "<b>Scheduler wake-up mismatch:</b> the 'time until next send' calculation did not follow the same "
    "head-of-line rule as the dequeue step, causing near-zero sleeps; both now use one shared rule.",
    "<b>Evaluation fairness:</b> the LSTM was first evaluated on history with earlier gaps collapsed; corrected so "
    "history contains the model's own earlier estimates, exactly as on the server.",
    "<b>Heavy deep-learning dependency:</b> PyTorch (over 500 MB) was replaced by a numpy LSTM, verified against "
    "numerical gradients, to keep the system deployable on low-cost hardware.",
])
H2("Individual contribution (Review 1 assignment)")
table([["Member", "Module"], ["Laksh Ahuja", "sensor_node.py — telemetry generation / loss simulation"],
       ["Anvay Sharma", "edge_gateway.py — QoS / classification"],
       ["Sreehari", "central_server.py + dashboard — reconstruction / API"]], [45, 125])
P("Ownership of the modules added in this revision is to be recorded by the team.", "small")
H2("Reference implementation files")
table([["File", "Role (reference numerals)"],
       ["common.py", "Record format, ports, classes, validation 210, rule classifier 222"],
       ["ocean_model.py", "Cyclone wind/pressure model and Gilbert–Elliott loss channel (Section 13.1)"],
       ["sensor_node.py", "Simulated buoy/radar node 110/112"], ["satellite_station.py", "Ground station 114 with 620/630/640"],
       ["edge_ai.py", "Feature extractor 620, risk scorer 630, ML trend classifier 224"],
       ["qos.py", "QoS scheduler 240 (241–248)"], ["edge_gateway.py", "Gateway 200 (205–260)"],
       ["lstm.py, reconstruction.py", "LSTM 700, reconstructor 420, forecasts for 430/450"],
       ["central_server.py, dashboard.html", "Server 400 (405–470), dashboard 500"],
       ["train_models.py, evaluate.py", "Model training; evaluation of Section 14"],
       ["run_demo.py, mininet_topology.py", "Launcher; Mininet embodiment"],
       ["hardware/", "ESP32 node 116, LoRa 132, serial bridge 134, hardware guide"]], [55, 115])

H1("APPENDIX G — DRAFTING NOTES", num=False)
P("This revision restructures the Review-1 student specification into the Form-2 complete-specification order "
  "(title, field, background, objects, summary, drawings, detailed description, claims, abstract) and updates "
  "it to the implemented system. The claims in Section 18 are a student draft written from the implemented "
  "mechanism; they have not been checked against prior art and should be reviewed by a registered patent agent "
  "before any filing. All numerical results are reproducible from the repository with "
  "<font name='DVM'>python evaluate.py</font>.", "small")


# =====================================================================  page decoration
def on_page(canv, doc):
    canv.saveState()
    canv.setFont("DV", 7.5)
    canv.setFillColor(GREY)
    w, h = A4
    canv.drawString(20 * mm, h - 12 * mm, "Student Patent Complete Specification | Form-2 Style")
    canv.drawRightString(w - 20 * mm, h - 12 * mm, f"Page {doc.page}")
    canv.drawString(20 * mm, 10 * mm, "Student Patent Complete Specification | Form-2 Style")
    canv.drawRightString(w - 20 * mm, 10 * mm, SHORT)
    canv.restoreState()


doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm,
                        bottomMargin=17 * mm, title="Complete Specification — " + SHORT,
                        author=", ".join(n for n, _ in APPLICANTS), subject="Indian Patent Form 2 (student draft)")
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print("wrote", OUT)
