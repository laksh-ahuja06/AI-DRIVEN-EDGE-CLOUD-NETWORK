"""Builds the three individual Review-3 reports as .fodt, then LibreOffice converts them to .odt and .pdf.

Run from the repository root:
    python docs/reports/make_figures.py docs/reports/evidence/live_run_output.txt docs/reports/evidence/train_log.txt
    python docs/reports/build_reports.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from odt import Doc  # noqa: E402

PF = os.path.join(REPO, "docs", "patent", "fig")
RF = os.path.join(HERE, "fig")
OUT = os.path.join(HERE, "out")
R = json.load(open(os.path.join(REPO, "results", "results.json")))
TITLE = "AI-Driven Edge–Cloud Network for Cyclone Prediction and Resilient Ocean Telemetry"
REPO_URL = "https://github.com/laksh-ahuja06/AI-DRIVEN-EDGE-CLOUD-NETWORK"
TEAM = [("Laksh Ahuja", "24BDS0212"), ("Anvay Sharma", "24BCE0824"), ("Sreehari", "24BDS0417")]

REFS = {
    "dvorak": 'V. F. Dvorak, "Tropical cyclone intensity analysis and forecasting from satellite imagery," *Monthly Weather Review*, vol. 103, no. 5, pp. 420–430, 1975.',
    "velden": 'C. Velden *et al.*, "The Dvorak tropical cyclone intensity estimation technique: A satellite-based method that has endured for over 30 years," *Bull. Amer. Meteor. Soc.*, vol. 87, no. 9, pp. 1195–1210, 2006.',
    "adt": 'T. L. Olander and C. S. Velden, "The Advanced Dvorak Technique: Continued development of an objective scheme to estimate tropical cyclone intensity using geostationary infrared satellite imagery," *Weather and Forecasting*, vol. 22, no. 2, pp. 287–298, 2007.',
    "pradhan": 'R. Pradhan, R. S. Aygun, M. Maskey, R. Ramachandran, and D. J. Cecil, "Tropical cyclone intensity estimation using a deep convolutional neural network," *IEEE Trans. Image Processing*, vol. 27, no. 2, pp. 692–702, 2018.',
    "holland": 'G. J. Holland, "An analytic model of the wind and pressure profiles in hurricanes," *Monthly Weather Review*, vol. 108, no. 8, pp. 1212–1218, 1980.',
    "lstm": 'S. Hochreiter and J. Schmidhuber, "Long short-term memory," *Neural Computation*, vol. 9, no. 8, pp. 1735–1780, 1997.',
    "grud": 'Z. Che, S. Purushotham, K. Cho, D. Sontag, and Y. Liu, "Recurrent neural networks for multivariate time series with missing values," *Scientific Reports*, vol. 8, art. 6085, 2018.',
    "brits": 'W. Cao, D. Wang, J. Li, H. Zhou, L. Li, and Y. Li, "BRITS: Bidirectional recurrent imputation for time series," in *Proc. NeurIPS*, 2018.',
    "adam": 'D. P. Kingma and J. Ba, "Adam: A method for stochastic optimization," in *Proc. ICLR*, 2015.',
    "gilbert": 'E. N. Gilbert, "Capacity of a burst-noise channel," *Bell System Technical Journal*, vol. 39, no. 5, pp. 1253–1265, 1960.',
    "elliott": 'E. O. Elliott, "Estimates of error rates for codes on burst-noise channels," *Bell System Technical Journal*, vol. 42, no. 5, pp. 1977–1997, 1963.',
    "shi": 'W. Shi, J. Cao, Q. Zhang, Y. Li, and L. Xu, "Edge computing: Vision and challenges," *IEEE Internet of Things Journal*, vol. 3, no. 5, pp. 637–646, 2016.',
    "satya": 'M. Satyanarayanan, "The emergence of edge computing," *Computer*, vol. 50, no. 1, pp. 30–39, 2017.',
    "diffserv": 'S. Blake, D. Black, M. Carlson, E. Davies, Z. Wang, and W. Weiss, "An architecture for differentiated services," IETF RFC 2475, 1998.',
    "red": 'S. Floyd and V. Jacobson, "Random early detection gateways for congestion avoidance," *IEEE/ACM Trans. Networking*, vol. 1, no. 4, pp. 397–413, 1993.',
    "drr": 'M. Shreedhar and G. Varghese, "Efficient fair queuing using deficit round-robin," *IEEE/ACM Trans. Networking*, vol. 4, no. 3, pp. 375–385, 1996.',
    "mininet": 'B. Lantz, B. Heller, and N. McKeown, "A network in a laptop: Rapid prototyping for software-defined networks," in *Proc. ACM HotNets*, 2010.',
    "coap": 'Z. Shelby, K. Hartke, and C. Bormann, "The Constrained Application Protocol (CoAP)," IETF RFC 7252, 2014.',
    "mqtt": 'A. Banks and R. Gupta (Eds.), "MQTT Version 3.1.1," OASIS Standard, 2014.',
    "lora": 'A. Augustin, J. Yi, T. Clausen, and W. M. Townsley, "A study of LoRa: Long range & low power networks for the Internet of Things," *Sensors*, vol. 16, no. 9, art. 1466, 2016.',
    "wmo": 'World Meteorological Organization, *WMO Atlas of Mortality and Economic Losses from Weather, Climate and Water Extremes (1970–2019)*, WMO-No. 1267, Geneva, 2021.',
    "imd": 'India Meteorological Department, "Cyclone eAtlas" and Regional Specialised Meteorological Centre (Tropical Cyclones) reports, New Delhi. [Online]. Available: https://rsmcnewdelhi.imd.gov.in',
}


class Refs:
    def __init__(self, keys):
        self.keys = keys

    def __call__(self, *ks):
        return "[" + ", ".join(str(self.keys.index(k) + 1) for k in ks) + "]"

    def write(self, d):
        d.h("References", 1, numbered=False)
        for i, k in enumerate(self.keys, 1):
            d.p(f"[{i}] {REFS[k]}", "Bullet")


def cover(d, name, reg, role, abstract, keywords):
    d.spacer()
    d.p("INDIVIDUAL PROJECT REPORT", "Center")
    d.p("Review 3 — Final Prototype, Report &amp; Viva (9/10/2026)".replace("&amp;", "&"), "Center")
    d.spacer()
    d.p(TITLE, "Title")
    d.spacer()
    d.table([["Student", "Register No.", "Team No.", "My role in the team"],
             [name, reg, "________", role]], [3.6, 3.0, 2.2, 8.2])
    d.p(f"**Team members:** {', '.join(f'{n} ({r})' for n, r in TEAM)}. **Source code:** {REPO_URL}", "Body")
    d.h("Abstract", 1, numbered=False)
    d.p(abstract)
    d.p(f"**Keywords:** {keywords}")
    d.page_break()


def results_tables():
    q = R["qos"]["runs"]
    qos_rows = [["Backbone", "Scheduler", "Critical delivered", "Critical avg / p95", "Normal delivered"]]
    for rate in ("1000", "1200", "1400", "2000"):
        for p in ("fifo", "priority"):
            c, n = q[rate][p]["CRITICAL"], q[rate][p]["NORMAL"]
            qos_rows.append([f"{rate} B/s", "FIFO" if p == "fifo" else "Priority QoS",
                             f"{100 * c['delivery_ratio']:.1f} %", f"{c['avg_ms']:.0f} / {c['p95_ms']:.0f} ms",
                             f"{100 * n['delivery_ratio']:.1f} %"])
    return qos_rows


# ============================================================================ LAKSH
def laksh():
    name, reg = TEAM[0]
    rf = Refs(["wmo", "imd", "holland", "diffserv", "red", "drr", "shi", "satya", "mininet", "coap", "mqtt", "lstm"])
    d = Doc(f"{reg} | {name} | R3 Individual Report", "Individual Project Report | Review 3",
            "AI-Driven Edge–Cloud Cyclone Prediction & Network Resilience", f"{reg}_LakshAhuja_R3", TITLE)
    cover(d, name, reg, "Central prediction server, live dashboard, QoS scheduler, cyclone/ocean model, "
          "demo launcher and the automated test suite",
          "Cyclone warnings depend on telemetry that must cross slow, lossy marine links at exactly the moment the "
          "weather is worst. Our team built a three-tier edge–cloud system in which ocean sensor nodes and a satellite "
          "ground station send compact data to an edge gateway, which forwards it by priority to a central prediction "
          "server. In this report I describe the parts I built: the central server that repairs lost packets, fuses "
          "in-situ, satellite and forecast risk and closes the alert loop back to the gateway; the token-bucket QoS "
          "scheduler that protects critical traffic with a work-conserving bandwidth reserve; the physics-based "
          "cyclone model that drives the simulation; the live WebSocket dashboard; the one-command launcher; and the "
          "28-test automated suite. On a congested 1200 B/s backbone the scheduler kept the 95th-percentile latency of "
          "critical packets at 356 ms compared with 49 s for first-in-first-out queuing, and at 1000 B/s it delivered "
          "100 % of critical packets against 77.3 %. In a 75-second live run the server raised the alert at about "
          "45 s, reconstructed 26 lost readings, concealed 6 overdue ones in real time and recovered 1 late packet.",
          "edge computing, quality of service, token bucket, cyclone monitoring, packet-loss recovery, FastAPI, WebSocket")

    d.h("Introduction")
    d.h("Problem statement", 2)
    d.p("Ocean and coastal sensors that track a developing cyclone send their readings over narrow, unreliable "
        "links; when a storm approaches, the volume of important data rises just as the link degrades, so the "
        "readings that matter most are delayed or lost.")
    d.h("Why it matters and who is affected", 2)
    d.p(f"India has a coastline of roughly 7,500 km and the Bay of Bengal is one of the most cyclone-prone basins "
        f"in the world; the 1999 Odisha super cyclone alone caused about 10,000 deaths {rf('imd')}. The WMO's "
        f"50-year disaster atlas lists tropical cyclones among the leading causes of both human and economic losses "
        f"from weather extremes {rf('wmo')}. The people affected are coastal and island communities and fishers, "
        f"who rely on timely warnings, and the disaster-management agencies that issue them. If the problem is left "
        f"unsolved, a warning system can show stale or missing values during the critical hours: in our own "
        f"first-in-first-out baseline on a congested link, 5 % of critical readings took longer than **49 s** to "
        f"arrive, and **23 %** were lost when the link was slightly undersized (Section 5).")
    d.h("Objectives of my part", 2)
    d.bullets([
        "Build a central server that tracks every node's sequence numbers, repairs gaps, publishes a fused cyclone-risk "
        "output and pushes the alert state back to the gateway.",
        "Design a backbone scheduler that serves critical traffic first without wasting capacity when the link is idle.",
        "Provide realistic test data (a cyclone that approaches, passes and recedes) and a dashboard that makes every "
        "mechanism visible during the demo.",
        "Make the whole project reproducible: one-command launch and an automated test suite.",
    ])

    d.h("Literature Review")
    d.p("Table 1 lists the works most relevant to my modules (networking, QoS, edge architecture and the physical "
        "storm model). The full 15-paper survey was presented in Review 1.")
    d.table([["Author / Year", "Method used", "Result", "Limitation for our problem"],
             [f"Blake et al., 1998 {rf('diffserv')}", "DiffServ: packets marked into classes, per-hop priority",
              "Scalable class-based QoS in IP networks", "Classes are static; no link to an external risk signal"],
             [f"Floyd & Jacobson, 1993 {rf('red')}", "RED: early random drops as the queue grows",
              "Avoids global synchronisation, keeps queues short", "Drops are class-blind; critical data can be dropped"],
             [f"Shreedhar & Varghese, 1996 {rf('drr')}", "Deficit round-robin fair queuing",
              "O(1) fairness between flows", "Fairness is the goal, not urgency; no alert mode"],
             [f"Shi et al., 2016 {rf('shi')}", "Edge computing vision and challenges",
              "Argues for processing near data sources", "Conceptual; no cyclone or lossy-link evaluation"],
             [f"Satyanarayanan, 2017 {rf('satya')}", "Cloudlets / edge tier architecture",
              "Lower latency and bandwidth via edge tier", "General purpose; no prioritisation policy"],
             [f"Holland, 1980 {rf('holland')}", "Analytic wind–pressure profile of hurricanes",
              "Widely used parametric storm model", "Needs parameters; not a telemetry system"],
             [f"Shelby et al., 2014; Banks & Gupta, 2014 {rf('coap', 'mqtt')}", "CoAP and MQTT lightweight IoT messaging",
              "Small headers, suits constrained devices", "No cyclone-aware scheduling at the gateway"],
             [f"Lantz et al., 2010 {rf('mininet')}", "Mininet network emulation",
              "Realistic topologies on one laptop", "Tool only; QoS policy must be supplied"]],
            [3.6, 4.3, 4.3, 4.8], "Literature most relevant to my modules")
    d.p("**Gap my part fills:** existing QoS schemes classify traffic statically and either drop blindly (RED) or "
        "share fairly (DRR). None ties the priority to a live cyclone-risk signal coming back from the prediction "
        "server, and none keeps a small reserve for critical packets while staying work-conserving. On the server "
        "side, the generic edge papers do not combine gap repair, real-time concealment and risk fusion with a "
        "feedback loop to the network.")

    d.h("Methodology")
    d.h("System overview", 2)
    d.p("The system has three tiers (Figure 1): sensing nodes, an edge gateway and the central server with the "
        "dashboard. My modules are the scheduler inside the gateway, the whole central server and dashboard, and "
        "the ocean model that feeds the sensors.")
    d.figure(os.path.join(PF, "fig01.png"), "Overall architecture (reference numerals as in our patent "
             "specification); my modules: QoS scheduler 240 inside 200, server 400, dashboard 500", 13.5)
    d.h("QoS scheduler design (qos.py)", 2)
    d.p("The backbone is modelled as a token bucket: credit accrues at the link rate r (bytes per second) up to a cap, "
        "and each packet costs its JSON size plus 28 bytes of UDP/IP header. Three queues (CRITICAL, NORMAL, "
        "NON_ESSENTIAL) are served in strict priority. During a cyclone alert two extra rules apply (Figure 2):")
    d.bullets(["**Critical reserve:** a NORMAL or NON_ESSENTIAL packet may only be sent if at least R = 700 bytes of "
               "credit remain afterwards, so the next critical packet never waits behind it.",
               "**Congestion-gated shedding:** NON_ESSENTIAL packets are rejected only if more than one second of "
               "traffic is already queued; with spare capacity they are still delivered."])
    d.figure(os.path.join(PF, "fig07.png"), "QoS scheduler: per-class queues, strict-priority selector, token "
             "bucket with critical reserve R", 13.5)
    d.h("Central server design (central_server.py)", 2)
    d.p("Input → process → output: a UDP listener receives each record → it is validated and routed by kind → for "
        "sensor records the server compares the sequence number with the last one (gap, duplicate, late packet or "
        "reboot) → gaps of up to 30 readings are filled by the LSTM reconstructor → a risk score is computed "
        "(50 % wind, 35 % pressure depression, 15 % pressure tendency) → the fused risk is "
        "max(in-situ, 0.9 × satellite, 0.8 × forecast) with an alert hysteresis of 60 on / 50 off → the state is "
        "served over REST/WebSocket and sent back to the gateway every 2 s. A separate 0.25 s loop publishes a "
        "provisional forecast when a node's packet is overdue by more than 2.5 times its usual interval.")
    d.figure(os.path.join(PF, "fig06.png"), "Server ingest, reconstruction and concealment flowchart (S601–S610)", 12.5)
    d.h("Cyclone model (ocean_model.py)", 2)
    d.p(f"Wind follows a modified Rankine profile and pressure follows the Holland profile {rf('holland')} as a "
        "vortex approaches, passes and recedes; AR(1) gusts, a diurnal temperature cycle and rain cooling are added "
        "(Figure 4). The same model generates the LSTM training data, so the simulation and the learning use "
        "consistent physics.")
    d.figure(os.path.join(RF, "L_ocean_trace.png"), "One cyclone passage from ocean_model.py; wind crosses "
             "60 km/h and pressure drops below 990 hPa near closest approach", 13)
    d.h("Justification of design choices", 2)
    d.table([["Decision", "Alternatives considered", "Chosen", "Reason"],
             ["Backbone scheduling", "FIFO; fixed bandwidth cap per class; weighted fair queuing",
              "Strict priority + token bucket + critical reserve", "Lowest critical latency; a fixed cap measurably hurt "
              "latency below saturation; WFQ guarantees fairness, not urgency"],
             ["Server framework", "Flask; Node.js; Django", "FastAPI + uvicorn", "Async WebSocket support next to a UDP "
              "thread; automatic API docs; same language as the AI code"],
             ["Transport to server", "TCP; MQTT broker; UDP", "UDP datagrams", "Loss must be visible to be handled; no "
              "retransmission delay; MQTT kept as an embodiment"],
             ["Dashboard update", "Polling every 2 s; server-sent events; WebSocket", "WebSocket with polling fallback",
              "Push every 1 s; still works if the WebSocket library is missing"],
             ["Test data", "Random walk; recorded buoy files; physics model", "Rankine + Holland physics model",
              "Realistic storm shape with known truth; real archives planned"]],
            [3.0, 4.6, 3.8, 5.6], "Design choices for my modules")

    d.h("Implementation")
    d.table([["File", "Lines", "Key functions / classes", "What I implemented"],
             ["central_server.py", "417", "ServerState.ingest, _ingest_sensor, conceal_overdue, predict, udp_listener, "
              "background_loop", "Gap / late / duplicate / reboot handling, real-time concealment, risk fusion, "
              "feedback, 9 REST endpoints + WebSocket"],
             ["qos.py", "178", "TokenBucket, QoSScheduler.enqueue/_head/dequeue/next_ready_in",
              "Strict priority, reserve, shedding, FIFO baseline, per-class statistics"],
             ["ocean_model.py", "146", "OceanNode, CycloneParams, GilbertElliottLink",
              "Storm physics and bursty loss channel"],
             ["dashboard.html", "233", "render(), drawSeries(), WebSocket + polling fallback",
              "Live banner, KPIs, tables, canvas charts, satellite thumbnail"],
             ["run_demo.py", "121", "start(), main()", "Starts 6 processes, waits for health, prints status, clean shutdown"],
             ["tests/", "300", "28 pytest cases", "Unit + integration tests for every module"]],
            [3.2, 1.3, 6.0, 6.5], "Files I implemented (line counts from the repository)")
    d.p("The scheduler is written as pure logic with an injected clock, so the *same* class runs inside the live "
        "gateway and inside the discrete-event evaluation. The core decision is only a few lines:")
    d.code(["def _head(self):",
            "    for q in self._candidates():            # CRITICAL, NORMAL, NON_ESSENTIAL",
            "        if q:",
            "            _, cls, size, _ = q[0]",
            "            reserve = self.reserve_bytes if (self.alert and cls != CRITICAL) else 0",
            "            return q, size + reserve",
            "    return None, None"])
    d.p("The dashboard (Figure 5) receives the whole server snapshot once per second over a WebSocket; if the "
        "WebSocket library is missing it falls back to polling the `/snapshot` endpoint.")
    d.figure(os.path.join(REPO, "docs", "dashboard.png"), "Live dashboard during an active alert (my implementation)", 15)

    d.h("Testing and Results")
    d.h("Requirements and test setup", 2)
    d.table([["Requirement (benchmark)", "Test setup", "Result", "Met?"],
             ["Critical p95 latency < 1 s on a congested backbone", "Discrete-event run, 300 s, 4 buoys + satellite, "
              "offered 1510 B/s, link 1000–2000 B/s", "305–407 ms (QoS) vs 14–66 s (FIFO)", "Yes"],
             ["Critical delivery ≥ 99 % under congestion", "Same, 225 critical packets per run", "100 % (QoS) vs 77.3 % (FIFO at 1000 B/s)", "Yes"],
             ["No capacity wasted when the link is idle", "Same, 2000 B/s link", "Identical to FIFO, 0 shed", "Yes"],
             ["Alert raised during a cyclone", "Live 75 s run, 3 nodes, 12 % bursty loss", "Alert at ≈45 s; risk 77–100", "Yes"],
             ["Dashboard update ≤ 2 s", "Browser on live run", "WebSocket push every 1 s", "Yes"],
             ["All automated tests pass", "pytest, 28 cases", "28 passed in 1.35 s", "Yes"]],
            [4.6, 5.0, 4.6, 1.4], "Benchmarks for my modules")
    d.h("QoS results", 2)
    d.table(results_tables(), [2.3, 3.0, 3.2, 4.0, 3.2], "Scheduler comparison (simulated clock, same code as gateway)")
    d.figure(os.path.join(PF, "fig13.png"), "Critical p95 latency (log scale) and delivery ratio, FIFO vs our QoS", 14)
    d.h("Live end-to-end run", 2)
    d.p("Figure 7 is plotted from the status lines my launcher printed during a 75-second run "
        "(`docs/reports/evidence/live_run_output.txt`). The server received 268 packets, repaired 26 lost readings, "
        "concealed 6 overdue readings in real time, swapped in 1 late packet, and measured a gateway-to-server "
        "critical p95 latency of 388 ms; the satellite stream used 27,095 bytes instead of 52.4 MB (99.948 % less).")
    d.figure(os.path.join(RF, "L_demo_timeline.png"), "Live run: fused risk, alert window and cumulative counters", 13.5)
    d.h("Failures found and fixed", 2)
    d.table([["What failed", "Diagnosis", "Change", "Retest result"],
             ["Evaluation hung forever", "`next_ready_in()` assumed a capped NORMAL queue could be skipped while "
              "`dequeue()` did not; the simulation advanced by nanoseconds", "Both functions now share one `_head()` rule",
              "Run completes; dedicated test `test_next_ready_in_is_consistent_with_dequeue`"],
             ["A 50 % cap on NORMAL traffic made critical latency *worse* below saturation",
              "Cap built a NORMAL backlog that drained in bursts and emptied the token bucket", "Replaced the cap with "
              "the 700-byte critical reserve", "At 1600 B/s critical latency went from 116 ms avg back to 0"],
             ["Dashboard stuck on 'polling' with empty charts", "WebSocket returned 404 because the `websockets` "
              "package was missing; fallback polled `/predict`, which lacks series data",
              "Added `/snapshot` endpoint and listed `websockets` in requirements", "Live WebSocket and full fallback both verified in a browser"],
             ["One of my tests failed (21 of 30 packets sent)", "The test switched the alert on before queueing, so "
              "shedding correctly removed 9 packets", "Test now raises the alert after the backlog exists", "28/28 pass"],
             ["Traceback noise on Ctrl+C in logs", "Child processes received SIGINT without handlers",
              "Clean KeyboardInterrupt handling in every component", "Logs end with a clean 'stopped' line"]],
            [3.3, 4.5, 4.2, 4.0], "Failures and fixes in my modules")

    d.h("Live Demonstration")
    d.numbered(["Run `python run_demo.py` and open http://127.0.0.1:8000 (input: 3 simulated nodes + satellite).",
                "0–15 s: green banner, NORMAL traffic, flat charts.",
                "≈30–45 s: pressure falls, packets turn CRITICAL, banner turns red; the QoS table shows CRITICAL waiting "
                "far less than NORMAL / NON_ESSENTIAL.",
                "Throughout: yellow dots appear where packets were lost and repaired; hollow dots for real-time guesses.",
                "Close-up: `/predict` and `/metrics` in the browser; then `python -m pytest -q` (28 passed).",
                "Baseline contrast: `python run_demo.py --scheduler fifo --backbone-bps 1000`."])
    video_plan(d, "laksh")

    d.h("Feasibility (Five Dimensions)")
    d.table([["Dimension", "Evidence"],
             ["Technical", "All benchmarks in the Section 5 benchmark table met; 28/28 tests pass; full run on one laptop core."],
             ["Economic", "Software cost ₹0 (Python, FastAPI, numpy are open source). Server runs on an existing laptop; "
              "a small cloud VM would cost roughly ₹400–800 per month (our Review 1 estimate of US$5–10). Hardware nodes "
              "≈₹800 each (see teammate's report). Bandwidth saving of 99.95 % on imagery directly reduces paid "
              "satellite airtime."],
             ["Social", "Benefits coastal communities with the weakest connectivity. Formal user feedback has not yet "
              "been collected; we will record faculty/peer feedback at the review: ____________"],
             ["Environmental", "No new hardware for the server tier; less data transmitted means less radio energy at "
              "the edge; dev boards are reusable."],
             ["Operational / Safety", "One-command start, health endpoint, automatic reboot detection, input validation "
              "rejects corrupt packets; no personal data handled."]],
            [3.2, 13.8], "Feasibility of the system with emphasis on my tier")

    d.h("Comparison with Literature")
    d.table([["Parameter", "Existing work", "Our project", "Improved?"],
             ["Priority basis", f"Static class marking (DiffServ) {rf('diffserv')}", "Class + live alert from server feedback", "Yes"],
             ["Behaviour under congestion", f"Random early drop, class-blind (RED) {rf('red')}",
              "Only NON_ESSENTIAL shed, only when backlog > 1 s", "Yes, for critical data"],
             ["Use of spare capacity", f"Fair share between flows (DRR) {rf('drr')}",
              "Work-conserving; reserve only during alert", "Comparable"],
             ["Edge architecture", f"Vision-level (Shi et al.) {rf('shi')}", "Running 3-tier prototype with measured latency",
              "Yes (concrete)"],
             ["Storm model fidelity", f"Holland profile with real best-track parameters {rf('holland')}",
              "Same profile with randomised parameters, not fitted to real storms", "No"]],
            [3.4, 5.2, 5.6, 2.8], "Comparison with five papers from the Review 1 survey")
    d.p("Where we did not improve: our storm model and all results use simulated data, and the scheduler has been "
        "tested on one gateway only; RED and DRR are proven at Internet scale, ours is not.")

    d.h("Scalability and Next Steps")
    d.bullets(["**Scale:** the server state is per node, so hundreds of nodes fit in memory; beyond that, the UDP "
               "listener can be sharded by node ID and the time-series store moved to a database (e.g. TimescaleDB).",
               "**Deployment:** containerise server and gateway, run the server on a cloud VM, gateways on Raspberry Pis "
               "at coastal sites; authentication on the API and HMAC-signed packets.",
               "**Improvements:** (1) replay real buoy archives (INCOIS / NOAA) through the pipeline; (2) adaptive reserve "
               "sized from measured critical arrival rate; (3) push alerts to SMS/mobile."])

    progress(d, "laksh")
    my_contribution(d, name, "laksh")
    d.h("Viva Preparation")
    viva(d, [("Why UDP and not TCP?", "Retransmission would add delay and hide loss; we expose loss and handle it with "
              "priority and reconstruction."),
             ("What happens if R (the reserve) is set to 0?", "Critical packets can wait behind a normal packet that "
              "just used the credit; with R too large normal traffic is throttled even when idle."),
             ("Why hysteresis on the alert?", "Without it the alert would flicker when risk hovers around 60."),
             ("How does the server detect loss?", "From per-node sequence numbers; a jump means missing packets."),
             ("What did you personally build?", "The server, scheduler, ocean model, dashboard, launcher and tests.")])
    d.h("Conclusion")
    d.p("My modules turn the edge–cloud idea into a measurable system: the scheduler protects critical cyclone "
        "telemetry under congestion without wasting idle capacity, the server keeps a continuous picture despite "
        "packet loss and closes the alert loop, and the dashboard and tests make every claim demonstrable. The main "
        "limitation is that all evidence comes from simulation; validating with real buoy data is the next step.")
    rf.write(d)
    appendices(d, "laksh")
    return d, "24BDS0212_LakshAhuja_R3_Report"


# ============================================================================ ANVAY
def anvay():
    name, reg = TEAM[1]
    rf = Refs(["wmo", "imd", "dvorak", "velden", "adt", "pradhan", "lstm", "grud", "adam", "shi", "diffserv"])
    d = Doc(f"{reg} | {name} | R3 Individual Report", "Individual Project Report | Review 3",
            "AI-Driven Edge–Cloud Cyclone Prediction & Network Resilience", f"{reg}_AnvaySharma_R3", TITLE)
    cover(d, name, reg, "Edge AI (satellite feature extraction and ML early-warning classifier), edge gateway, "
          "LSTM implementation, evaluation harness, trained models and run logs",
          "Our project is a cyclone-monitoring network in which sensing nodes and a satellite ground station report to "
          "an edge gateway that forwards data by importance to a central prediction server. My work is the "
          "intelligence at the edge and the evidence behind it. I implemented the edge-AI module, which reduces a "
          "2.1 MB four-band satellite frame to a roughly 1 KB feature record using Dvorak-inspired cues, and a "
          "logistic-regression classifier that predicts a threshold breach within the next ten readings from the "
          "trend of a node's data; the edge gateway that validates, classifies and forwards every packet; a long "
          "short-term memory network written from scratch in numpy with backpropagation through time and Adam; and "
          "the evaluation harness that produced all reported numbers. The classifier warned on average 16.5 readings "
          "before the fixed thresholds were crossed, raising recall from 0.70 to 0.99 at a precision of 0.72. The LSTM "
          "reached a validation error 66 % below a no-change forecast, and its gradients matched numerical estimates "
          "to a relative error of 3 × 10⁻⁷. Edge feature extraction saved 99.95 % of satellite bandwidth.",
          "edge AI, logistic regression, LSTM, Dvorak technique, satellite imagery, early warning, evaluation")

    d.h("Introduction")
    d.h("Problem statement", 2)
    d.p("A cyclone-warning network must decide, at the edge and within milliseconds, which data is urgent; if it "
        "can only react once a dangerous value has been measured, and if it ships every multi-megabyte satellite "
        "image unprocessed, warnings arrive late and the backbone chokes.")
    d.h("Why it matters and who is affected", 2)
    d.p(f"Tropical cyclones are among the deadliest and costliest weather extremes recorded by the WMO {rf('wmo')}, and "
        f"India's east coast is repeatedly exposed {rf('imd')}. Fishing communities, coastal residents and the "
        f"authorities that order evacuations need warnings as early as possible. A threshold-only network gives "
        f"**zero** readings of lead time by definition, and a single raw satellite frame (2.1 MB) would occupy a "
        f"9.6 kbps link for about half an hour — the consequence is late or missing alerts.")
    d.h("Objectives of my part", 2)
    d.bullets(["Extract compact, explainable storm features from satellite frames at the ground station.",
               "Flag danger from the trend of the data, before thresholds are crossed, without hiding threshold breaches.",
               "Build the gateway that validates, classifies and hands every packet to the scheduler.",
               "Implement and verify the LSTM used for reconstruction, and measure every claim reproducibly."])

    d.h("Literature Review")
    d.table([["Author / Year", "Method used", "Result", "Limitation for our problem"],
             [f"Dvorak, 1975 {rf('dvorak')}", "Expert pattern analysis of satellite cloud features",
              "Operational intensity estimates worldwide", "Subjective, analyst-dependent"],
             [f"Velden et al., 2006 {rf('velden')}", "Review of 30 years of the Dvorak technique",
              "Explains strengths and error sources", "Needs trained analysts and full images"],
             [f"Olander & Velden, 2007 {rf('adt')}", "Advanced Dvorak Technique: objective IR scheme",
              "Automated intensity from geostationary IR", "Runs centrally on full-resolution imagery"],
             [f"Pradhan et al., 2018 {rf('pradhan')}", "Deep CNN on IR satellite images",
              "Learned intensity estimation with good accuracy", "GPU-heavy, needs large labelled datasets"],
             [f"Hochreiter & Schmidhuber, 1997 {rf('lstm')}", "LSTM recurrent network",
              "Learns long-range temporal dependencies", "Generic model; no telemetry pipeline"],
             [f"Che et al., 2018 {rf('grud')}", "GRU-D: RNN with missing-value decay",
              "Better accuracy on series with gaps", "Framework-heavy; offline clinical data"],
             [f"Kingma & Ba, 2015 {rf('adam')}", "Adam adaptive optimiser", "Fast, robust training", "Optimiser only"],
             [f"Shi et al., 2016 {rf('shi')}", "Edge computing vision", "Motivates processing near sources",
              "No concrete edge-AI evaluation"]],
            [3.6, 4.3, 4.3, 4.8], "Literature most relevant to my modules")
    d.p("**Gap my part fills:** objective Dvorak-style schemes and CNNs run centrally on full images; none sends "
        "only the features over a constrained link. Existing QoS classifiers use the current value only. My modules "
        "move a lightweight, explainable image analysis to the ground station and add a trend-based classifier at "
        "the gateway that runs on a Raspberry-class CPU with only numpy.")

    d.h("Methodology")
    d.figure(os.path.join(PF, "fig01.png"), "System architecture; my modules: edge AI (in 114 and 224) and the "
             "edge gateway 200", 13)
    d.h("Edge gateway pipeline (edge_gateway.py)", 2)
    d.p("Input → process → output (Figure 2): a datagram is received → parsed and validated (node ID, sequence "
        "number, numeric fields in physical ranges) → its node history buffer (last 6 readings) is updated → the rule "
        "classifier and the ML classifier both run → hybrid decision (CRITICAL if either says so) → the packet is "
        "annotated (class, ML probability, gateway timestamp) and handed to the QoS scheduler → forwarded. The "
        "gateway also accepts alert feedback from the server and notifies hardware nodes every 2 s.")
    d.figure(os.path.join(PF, "fig02.png"), "Edge gateway functional blocks (205–260)", 13.5)
    d.figure(os.path.join(PF, "fig05.png"), "Gateway method flowchart (S501–S512)", 12.5)
    d.h("ML early-warning classifier (edge_ai.QoSClassifier)", 2)
    d.p("Seven features are computed per reading: current wind and pressure, the per-reading trend of wind, pressure "
        "and temperature over the history window, and the distance of wind and pressure to their thresholds. A "
        "logistic regression with feature standardisation and class weighting outputs P(breach within 10 readings); "
        "labels come from 240 simulated scenarios in which the future is known.")
    d.h("Satellite feature extraction (edge_ai.extract_features)", 2)
    d.p(f"From the infrared band: cold-cloud fraction (< 220 K), coldest cloud top, coldness-weighted storm centre, "
        f"axisymmetry over eight angular sectors and eye contrast (warm centre minus eyewall). These mirror the cues "
        f"of the Dvorak technique {rf('dvorak', 'velden')}. The risk score is "
        f"40·cover·depth + 30·symmetry·cover + 30·eye, flagged at 60 (Figure 4). This part is classical, rule-based "
        f"image analysis; the learned components are the classifier and the LSTM.")
    d.figure(os.path.join(PF, "fig09.png"), "Features and risk extracted from frames of increasing storm intensity", 15)
    d.h("LSTM (lstm.py)", 2)
    d.p(f"A standard LSTM cell {rf('lstm')} with forget-gate bias 1, a linear read-out, mean-squared-error loss, "
        f"backpropagation through time, gradient clipping at norm 5 and the Adam optimiser {rf('adam')}. Input: 12 steps "
        f"× 6 features (normalised levels and first differences); output: the next change in wind, temperature and "
        f"pressure. Hidden size 32; about 5,100 parameters.")
    d.h("Justification of design choices", 2)
    d.table([["Decision", "Alternatives considered", "Chosen", "Reason"],
             ["Early-warning model", "Threshold rule only; random forest; small neural network", "Logistic regression "
              "+ rule (hybrid)", "Explainable weights, trains in < 1 s, runs on a Pi; rule guarantees no missed breach"],
             ["Satellite analysis", "Send raw frames; zlib compression; CNN intensity model", "Dvorak-style features at "
              "the edge", "99.95 % saving vs 17–22 % for zlib; no GPU or labelled real imagery needed"],
             ["Sequence model", "Linear interpolation; GRU; LSTM in PyTorch", "LSTM in numpy", "Captures dynamics; no "
              "550 MB framework; verifiable with a gradient check"],
             ["Optimiser", "SGD; RMSprop; Adam", "Adam with clipping", "Stable, fast convergence on small batches"],
             ["Evaluation", "Manual demo runs; live measurements only", "Scripted harness, held-out scenarios, same "
              "scheduler code with a simulated clock", "Reproducible numbers; fair baselines"]],
            [3.0, 4.6, 3.8, 5.6], "Design choices for my modules")

    d.h("Implementation")
    d.table([["File", "Lines", "Key functions / classes", "What I implemented"],
             ["edge_ai.py", "208", "extract_features, satellite_risk, trend_features, NodeHistory, QoSClassifier.fit/predict",
              "Image features, risk score, thumbnail, logistic regression (numpy)"],
             ["edge_gateway.py", "237", "Gateway.handle_packet, classify, forwarder, control_listener, stats_reporter",
              "Validation, hybrid classification, alert logic, feedback, node alerts, statistics"],
             ["lstm.py", "151", "LSTMRegressor.forward, loss_and_grads, adam_step, fit, save/load",
              "Complete LSTM with BPTT and Adam, no external DL framework"],
             ["evaluate.py", "396", "eval_recovery, simulate_qos, eval_classifier, eval_bandwidth, write_report",
              "Reproducible experiments → results/REPORT.md + plots"],
             ["models/", "2 files", "lstm_recon.npz, qos_classifier.npz", "Trained weights shipped with the code"],
             ["logs/", "9 files", "per-component logs + truth CSVs", "Run evidence used in all reports"]],
            [2.8, 1.4, 6.3, 6.5], "Files I implemented")
    d.p("The backward pass of the LSTM is the part most likely to hide a bug, so I verified it against a numerical "
        "gradient (central differences, ε = 10⁻⁶). The maximum relative error was 2.9 × 10⁻⁷, and the check is kept "
        "as an automated test.")
    d.code(["for z, i, f, o, g, c_prev, tc in reversed(cache):     # backprop through time",
            "    do = dh * tc",
            "    dc = dc + dh * o * (1 - tc ** 2)",
            "    da = concat([dc*g*i*(1-i), dc*c_prev*f*(1-f), do*o*(1-o), dc*i*(1-g**2)])",
            "    grads['W'] += z.T @ da;  dh = (da @ W.T)[:, n_in:];  dc = dc * f"])

    d.h("Testing and Results")
    d.table([["Requirement (benchmark)", "Test setup", "Result", "Met?"],
             ["Warn before threshold breach", "60 held-out scenarios × 190 readings", "Mean lead 16.5 readings (rule: 0)", "Yes"],
             ["Recall of upcoming breaches ≥ 0.95", "Same", "0.99 hybrid (rule 0.70)", "Yes"],
             ["Precision ≥ 0.70", "Same", "0.72", "Yes (narrowly)"],
             ["LSTM better than no-change forecast", "1,520 validation windows", "MSE 0.089 vs 0.265 (−66 %)", "Yes"],
             ["Gradient correctness", "Numerical check, all weight matrices", "rel. error 2.9 × 10⁻⁷", "Yes"],
             ["Satellite bandwidth reduction ≥ 95 %", "9 frames, 3 sizes", "99.80–99.99 %", "Yes"],
             ["Edge inference < 100 ms per 512² frame", "Laptop CPU", "≈13 ms", "Yes"],
             ["Gateway rejects corrupt packets", "Malformed JSON, out-of-range values", "Counted and dropped (unit test)", "Yes"]],
            [4.6, 4.8, 4.8, 1.8], "Benchmarks for my modules")
    c = R["classifier"]
    d.table([["Policy", "Precision", "Recall", "F1", "Mean lead (readings)", "Calm scenarios with false alarm"]] +
            [[m, c[m]["precision"], c[m]["recall"], c[m]["f1"], c[m]["mean_lead_readings"],
              f'{c[m]["calm_traces_with_false_alarm"]} of {c["calm_traces"]}'] for m in ("rule", "ml", "hybrid")],
            [2.4, 2.2, 2.0, 1.8, 3.6, 5.0], "Classifier results on held-out scenarios")
    d.figure(os.path.join(RF, "A_classifier_lead.png"), "Example scenario: ML probability crosses 0.5 fourteen "
             "readings before the rule fires", 13.5)
    d.figure(os.path.join(RF, "A_training_curve.png"), "LSTM training and validation error (from train_log.txt)", 12.5)
    d.p("In the live run the gateway forwarded 52 critical, 170 normal and 39 non-essential packets with no queue "
        "drops, shed 3 housekeeping packets during the alert, and flagged 29 packets as critical through the ML "
        "classifier before the rule would have (Figure 7).")
    d.figure(os.path.join(RF, "A_gateway_waits.png"), "Gateway waits per class in the live run (from my gateway statistics)", 12.5)
    d.h("Failures found and fixed", 2)
    d.table([["What failed", "Diagnosis", "Change", "Retest result"],
             ["PyTorch could not be used on target hardware", "≈550 MB download, too heavy for a Pi gateway",
              "Wrote the LSTM in numpy with BPTT and Adam", "Trains in 19 s; gradient check passes"],
             ["LSTM gap-repair looked worse than linear for wind at 10 % loss", "Evaluation fed the model a history with "
              "earlier gaps collapsed — not what the server does", "History now contains the model's own earlier "
              "estimates", "Fair comparison; honest result: equal for wind, better for pressure"],
             ["Satellite risk stayed near 0 for strong storms", "Synthetic cloud tops never reached the 220 K cold "
              "threshold, so cold-cloud cover was ≈0", "Re-calibrated cover normalisation with my teammate's imager fix",
              "Risk rises 0 → 6 → 48 → 70 → 93 with intensity"],
             ["Classifier raised false alarms", "Trend features fire on calm-day gusts", "Kept hybrid policy, reported "
              "the trade-off instead of tuning on test data", "3 of 9 calm scenarios; documented as a limitation"]],
            [3.3, 4.5, 4.2, 4.0], "Failures and fixes in my modules")

    d.h("Live Demonstration")
    d.numbered(["`python train_models.py` — show training output (≈20 s) and the saved models.",
                "`python run_demo.py` — open the dashboard; point to the ML probability column and the satellite panel.",
                "Open `logs/gateway.log` — show packets classified CRITICAL early and the 'alert ACTIVE' line.",
                "`python evaluate.py` — regenerate `results/REPORT.md` and walk through the classifier and bandwidth tables.",
                "`python -m pytest -q` — 28 passed, including the LSTM gradient test."])
    video_plan(d, "anvay")

    d.h("Feasibility (Five Dimensions)")
    d.table([["Dimension", "Evidence"],
             ["Technical", "All benchmarks in the Section 5 benchmark table met; models train in about 20 s on a laptop CPU; inference needs only numpy."],
             ["Economic", "No paid software or GPU; edge AI runs on existing hardware. Sending ≈1 KB instead of 2.1 MB "
              "per frame cuts satellite airtime cost by ≈99.95 %."],
             ["Social", "Earlier warnings directly benefit coastal residents; feedback from reviewers to be recorded: ____________"],
             ["Environmental", "No GPU training (low energy); smaller transmissions save radio energy at remote stations."],
             ["Operational / Safety", "Classifier is explainable (7 named features); rule kept as a safety floor so a "
              "threshold breach is never missed; gateway rejects malformed data."]],
            [3.2, 13.8], "Feasibility with emphasis on my modules")

    d.h("Comparison with Literature")
    d.table([["Parameter", "Existing work", "Our project", "Improved?"],
             ["Where image analysis runs", f"Centrally on full images (ADT) {rf('adt')}", "At the ground station; only ≈1 KB sent", "Yes"],
             ["Objectivity", f"Analyst-dependent (Dvorak) {rf('dvorak')}", "Fully automatic, explainable features", "Yes"],
             ["Intensity accuracy", f"CNN validated on real storms {rf('pradhan')}", "Not validated on real imagery", "No"],
             ["Missing-data model", f"GRU-D learns decay over gaps {rf('grud')}", "LSTM forecast anchored to next reading", "Comparable, simpler"],
             ["Compute needed", f"Deep-learning frameworks / GPU {rf('pradhan', 'grud')}", "numpy only, CPU, ≈5.1 k parameters", "Yes"]],
            [3.4, 5.2, 5.6, 2.8], "Comparison with five papers from the Review 1 survey")

    d.h("Scalability and Next Steps")
    d.bullets(["Run the feature extractor on real INSAT-3D/3DR infrared tiles from MOSDAC and recalibrate the thresholds.",
               "Replace logistic regression with gradient-boosted trees or a small temporal model, keeping the rule as a floor.",
               "Track model versions and retrain automatically from archived telemetry; quantise the LSTM for microcontrollers.",
               "Multiple gateways: share node histories so a node moving between gateways keeps its trend features."])

    progress(d, "anvay")
    my_contribution(d, name, "anvay")
    d.h("Viva Preparation")
    viva(d, [("Why logistic regression and not a deep model?", "Small, explainable, trains in seconds, runs on a Pi; "
              "the trend features carry most of the signal."),
             ("Why keep the rule in the hybrid policy?", "So a real threshold breach is never missed even if the ML is wrong."),
             ("Is the image analysis machine learning?", "No — it is Dvorak-inspired classical image processing; "
              "the classifier and the LSTM are the learned parts."),
             ("How did you know your LSTM gradients were right?", "Numerical gradient check, relative error 2.9 × 10⁻⁷."),
             ("What if the classifier threshold changes from 0.5?", "Lower → earlier warnings, more false alarms; higher → fewer false alarms, less lead.")])
    d.h("Conclusion")
    d.p("My modules give the network judgement at the edge: satellite frames shrink to the features that matter, "
        "and the gateway recognises an approaching storm from its trend well before thresholds are crossed. The LSTM "
        "and the evaluation harness make the reconstruction and every number in our reports reproducible. The key "
        "limitations — synthetic imagery and some false alarms — are stated openly and define the next steps.")
    rf.write(d)
    appendices(d, "anvay")
    return d, "24BCE0824_AnvaySharma_R3_Report"


# ============================================================================ SREEHARI
def sreehari():
    name, reg = TEAM[2]
    rf = Refs(["wmo", "imd", "gilbert", "elliott", "holland", "brits", "grud", "lstm", "lora", "coap", "dvorak"])
    d = Doc(f"{reg} | {name} | R3 Individual Report", "Individual Project Report | Review 3",
            "AI-Driven Edge–Cloud Cyclone Prediction & Network Resilience", f"{reg}_Sreehari_R3", TITLE)
    cover(d, name, reg, "Sensing layer: hardware nodes (ESP32 firmware, LoRa option), sensor simulator, satellite "
          "ground station, lost-telemetry reconstruction and model training",
          "Cyclone monitoring starts at the sensors, and our system can only be as good as the data they deliver over "
          "lossy marine links. I built the sensing side of our three-tier edge–cloud network and the recovery of "
          "data lost on the way. This includes the sensor-node simulator with a bursty Gilbert–Elliott loss channel and "
          "a ground-truth log, the satellite ground station that synthesises four-band 16-bit frames and transmits only "
          "edge features, the ESP32 firmware for real buoy nodes with sea-level pressure correction and an alert "
          "LED/buzzer, an optional LoRa link with a serial bridge, the reconstruction module that repairs gaps with an "
          "LSTM forecast anchored to the next received reading, and the training pipeline. On packets actually lost "
          "during a live run, the reconstruction's pressure error was 0.25 hPa against 0.44 hPa for linear "
          "interpolation. For real-time concealment the forecast cut error versus holding the last value by about "
          "27 % for wind and 53–57 % for pressure. The loss model reproduced its target loss rate to within 1 %.",
          "sensor networks, ESP32, LoRa, bursty packet loss, LSTM imputation, synthetic satellite imagery")

    d.h("Introduction")
    d.h("Problem statement", 2)
    d.p("Buoys and coastal stations lose packets in bursts when storms bring rain fade and interference, so the "
        "monitoring centre sees gaps exactly in the hours when the readings change fastest.")
    d.h("Why it matters and who is affected", 2)
    d.p(f"Tropical cyclones are a leading cause of weather-related deaths and losses worldwide {rf('wmo')}, and Indian "
        f"coastal states face severe storms most years {rf('imd')}. Gaps in buoy data hurt forecasters, who lose the "
        f"pressure trend that signals intensification, and coastal residents, whose warnings depend on it. In our "
        f"live run 10 of 76 readings from one buoy were lost (13 %), three of them in a row right as pressure "
        f"began to fall below 995 hPa (Section 5).")
    d.h("Objectives of my part", 2)
    d.bullets(["Generate realistic telemetry and loss patterns, and record the ground truth so recovery can be measured.",
               "Provide a satellite ground station that produces large frames and sends only features.",
               "Design low-cost hardware nodes that are drop-in replacements for the simulator.",
               "Reconstruct lost readings better than straight-line interpolation, and train the model reproducibly."])

    d.h("Literature Review")
    d.table([["Author / Year", "Method used", "Result", "Limitation for our problem"],
             [f"Gilbert, 1960 {rf('gilbert')}", "Two-state Markov burst-noise channel", "Captures error bursts", "Channel model only"],
             [f"Elliott, 1963 {rf('elliott')}", "Error-rate estimates for burst channels", "Practical parameter fitting", "Not applied to IoT telemetry"],
             [f"Cao et al., 2018 {rf('brits')}", "BRITS: bidirectional RNN imputation", "State-of-the-art imputation", "Offline, needs whole series; heavy framework"],
             [f"Che et al., 2018 {rf('grud')}", "GRU-D with decay for missing values", "Improves prediction with gaps", "Clinical data; not real-time"],
             [f"Hochreiter & Schmidhuber, 1997 {rf('lstm')}", "LSTM network", "Learns temporal dynamics", "Generic model"],
             [f"Holland, 1980 {rf('holland')}", "Parametric hurricane pressure profile", "Realistic storm pressure field", "Needs storm parameters"],
             [f"Augustin et al., 2016 {rf('lora')}", "Study of LoRa range and throughput", "Long range at very low data rate", "Low throughput; duty-cycle limits"],
             [f"Shelby et al., 2014 {rf('coap')}", "CoAP for constrained devices", "Compact messaging for MCUs", "No loss recovery at the receiver"]],
            [3.6, 4.3, 4.3, 4.8], "Literature most relevant to my modules")
    d.p("**Gap my part fills:** imputation research (BRITS, GRU-D) works offline on complete series and needs large "
        "frameworks; channel models are rarely used to generate realistic test data for IoT recovery. My modules "
        "combine a bursty channel model with ground-truth logging and an online, lightweight reconstruction that "
        "works both after a gap closes and while a packet is overdue, on hardware costing about ₹800 per node.")

    d.h("Methodology")
    d.figure(os.path.join(PF, "fig01.png"), "System architecture; my modules: sensing nodes 110–116 and the "
             "reconstruction used by server 400", 13)
    d.h("Sensor node and loss model (sensor_node.py)", 2)
    d.p(f"Each simulated node takes one reading per second from the cyclone model, numbers it, applies a loss "
        f"decision, sends the surviving packet over UDP, and writes every reading — lost or not — to a truth CSV. "
        f"Loss follows the Gilbert–Elliott model {rf('gilbert', 'elliott')}: a 'good' state with rare loss and a 'bad' "
        f"(rain-fade) state with heavy loss, with transition probabilities set from the target mean loss and "
        f"burstiness (Figure 2). Every fifth reading a housekeeping packet (battery, RSSI) is also sent.")
    d.figure(os.path.join(RF, "S_loss_pattern.png"), "Independent vs bursty loss at the same target rate", 14)
    d.h("Satellite ground station (satellite_station.py)", 2)
    d.p("Frames are synthesised with formulas, not with an AI generator: smooth random background cloud, spiral arms "
        "from cos(2θ + 6 ln r), a central dense overcast and, above intensity 0.65, a clear eye. Four 16-bit bands "
        "(visible, infrared, water vapour, near-IR) at 512 × 512 pixels give 2.1 MB per frame (Figure 3). Each frame "
        "is passed to the feature extractor (teammate's edge-AI module) and only the ≈1 KB record is sent.")
    d.figure(os.path.join(RF, "S_satellite_bands.png"), "The four bands of one synthetic frame", 15)
    d.h("Anchored LSTM reconstruction (reconstruction.py)", 2)
    d.p("For a gap of n readings, the LSTM forecasts n + 1 steps from the repaired history; the error at the last "
        "step against the reading actually received is spread linearly back over the gap: "
        "estimate_k = f_k + (k / (n + 1)) · (x_next − f_(n+1)). The estimates therefore follow the learned dynamics "
        "and join the real reading without a jump (Figure 4). When no later reading exists yet, the raw forecast is "
        "used as a provisional value.")
    d.figure(os.path.join(PF, "fig08.png"), "Anchored LSTM estimate vs linear interpolation on a gap near closest approach", 13.5)
    d.h("Hardware node (hardware/)", 2)
    d.p("An ESP32 reads a BMP280 (temperature, pressure) over I²C and a wind input (potentiometer or reed-switch "
        "cup anemometer), converts station pressure to sea-level pressure using the configured altitude, and sends "
        "the same JSON packet as the simulator. It listens on UDP 9004 and drives an LED and buzzer when the gateway "
        "reports an alert; the BOOT button toggles a storm mode for indoor demos (Figure 5).")
    d.figure(os.path.join(PF, "fig11.png"), "Hardware sensor node 116", 12.5)
    d.table([["Signal", "Module pin", "ESP32 pin", "Note"],
             ["Power", "BMP280 VCC / GND", "3V3 / GND", "3.3 V only"],
             ["I²C data / clock", "BMP280 SDA / SCL", "GPIO21 / GPIO22", "address 0x76 or 0x77"],
             ["Wind", "Potentiometer wiper or reed switch", "GPIO34 (ADC) / GPIO27 (interrupt)", "WIND_POT selects"],
             ["Alert LED", "On-board LED", "GPIO2", "blinks during alert"],
             ["Buzzer", "BC547 base via 1 kΩ", "GPIO25", "buzzer on 5 V via transistor"],
             ["Storm mode", "BOOT button", "GPIO0", "ramps pressure −35 hPa, wind +70 km/h"]],
            [3.0, 4.6, 4.6, 4.8], "Wiring of the ESP32 node")
    d.h("Justification of design choices", 2)
    d.table([["Decision", "Alternatives considered (approx. cost)", "Chosen", "Reason"],
             ["Microcontroller", "Arduino Uno + ESP8266 (≈₹700); Raspberry Pi Pico W (≈₹550); ESP32 (≈₹400)", "ESP32",
              "Built-in Wi-Fi, cheapest, enough RAM for JSON, deep sleep"],
             ["Pressure sensor", "DHT22 (no pressure, ≈₹250); BME280 (≈₹400); BMP280 (≈₹120)", "BMP280",
              "Pressure is the key cyclone signal; BME280 only adds humidity"],
             ["Radio link", "GSM/4G module (SIM cost); LoRa SX1278 (≈₹400); Wi-Fi (built in)", "Wi-Fi, LoRa optional",
              "Free on campus for the demo; LoRa adds a truly constrained link"],
             ["Loss model", "Independent coin flips; trace replay; Gilbert–Elliott", "Gilbert–Elliott",
              "Reproduces bursty rain-fade loss with two parameters"],
             ["Gap repair", "Linear interpolation; GRU-D / BRITS; anchored LSTM", "Anchored LSTM (linear fallback)",
              "Works online and in real time; light enough for the server and a Pi"]],
            [3.0, 5.6, 3.0, 5.4], "Design choices for my modules")

    d.h("Implementation")
    d.table([["File", "Lines", "Key functions", "What I implemented"],
             ["sensor_node.py", "121", "run_sensor()", "Readings, sequence numbers, GE/independent loss, housekeeping, truth CSV"],
             ["satellite_station.py", "173", "SyntheticImager.frame, intensity_at, build_record, run_station",
              "4-band frame synthesis, storm life cycle, PNG export, byte accounting"],
             ["reconstruction.py", "91", "Reconstructor.forecast, fill_gap, make_inputs, linear_fill",
              "Anchored gap repair, real-time forecast, linear fallback"],
             ["train_models.py", "109", "simulate_traces, lstm_dataset, qos_dataset, main",
              "280 random scenarios → 22,560 LSTM windows + classifier data"],
             ["hardware/esp32_buoy", "189", "setup, loop, checkAlerts, readWindKmh", "Wi-Fi node firmware"],
             ["hardware/lora_*, serial_bridge.py", "220", "LoRa TX/RX sketches, parse_line()", "Optional LoRa link → UDP"],
             ["hardware/README.md", "—", "BOM, wiring, flashing, demo script", "College-scale build guide"]],
            [3.4, 1.3, 5.5, 6.8], "Files I implemented")
    d.table([["Item", "Qty", "Approx. ₹ each", "Purpose"],
             ["ESP32 DevKit V1 (ESP-WROOM-32)", "2", "350–450", "Node microcontroller with Wi-Fi"],
             ["BMP280 module (I²C)", "2", "100–150", "Temperature + pressure"],
             ["10 kΩ potentiometer / reed switch + magnet", "2", "10–40", "Wind input (demo knob or cup anemometer)"],
             ["Active buzzer + BC547 + 1 kΩ resistor", "2", "20–30", "Alert sound"],
             ["Breadboard, jumper wires, USB data cables", "—", "300–400", "Assembly and power"],
             ["Optional: SX1278 LoRa modules + antennas (pair)", "1", "800–1,100", "Constrained radio link"],
             ["Optional: 6 V solar panel + TP4056 + 18650 cell", "1", "450–600", "Self-powered buoy"],
             ["**Two-node prototype (without options)**", "", "**≈1,600–2,200**", ""]],
            [6.4, 1.2, 2.8, 6.6], "Bill of materials (college-scale prices, 2025–26)")
    d.p("A detail that mattered on hardware: at our campus altitude (≈216 m) a BMP280 reads about 988 hPa, which is "
        "below our 990 hPa cyclone threshold. The firmware therefore applies the barometric correction before sending:")
    d.code(["float seaLevel = station / pow(1.0 - ALTITUDE_M / 44330.0, 5.255);"])

    d.h("Testing and Results")
    d.table([["Requirement (benchmark)", "Test setup", "Result", "Met?"],
             ["Loss model hits its target rate (±1 %)", "100,000 packets at 5/10/20 %", "4.98 / 9.94 / 19.73 %", "Yes"],
             ["Losses are bursty", "Same", "Mean burst 1.65–1.77 packets", "Yes"],
             ["Gap repair ≤ linear error for pressure", "60 held-out scenarios, 3 loss rates", "7–15 % lower", "Yes"],
             ["Gap repair ≤ linear error for wind", "Same", "Equal (±4 %)", "Partly"],
             ["Real-time forecast better than hold-last", "Same", "−27 % wind, −53–57 % pressure", "Yes"],
             ["Reconstruct real live-run losses", "BUOY_07 truth CSV, 10 lost of 76", "0.25 hPa vs 0.44 hPa (linear)", "Yes"],
             ["Frame size reduction ≥ 95 %", "512² frames", "2.10 MB → ≈1.04 KB (99.95 %)", "Yes"],
             ["Firmware compiles", "g++ syntax check with stub headers", "3/3 sketches pass; full ESP32 build pending", "Partly"]],
            [4.6, 4.8, 4.8, 1.8], "Benchmarks for my modules")
    rec = R["recovery"]
    rows = [["Loss", "Variable", "Linear gap repair", "LSTM gap repair", "Hold-last (real time)", "LSTM forecast (real time)"]]
    for loss, rr in rec.items():
        for v in ("wind", "pressure"):
            rows.append([loss, v, rr["linear"][v]["mae"], rr["lstm"][v]["mae"], rr["hold"][v]["mae"], rr["forecast"][v]["mae"]])
    d.table(rows, [1.6, 2.0, 3.0, 3.0, 3.6, 3.8], "Mean absolute error (km/h, hPa) under bursty loss")
    d.figure(os.path.join(PF, "fig14.png"), "Reconstruction error by method and loss rate", 14)
    d.figure(os.path.join(RF, "S_truth_vs_recon.png"), "Packets really lost in the live run and my reconstruction", 13.5)
    d.h("Failures found and fixed", 2)
    d.table([["What failed", "Diagnosis", "Change", "Retest result"],
             ["Indoor pressure ≈988 hPa looked like a cyclone", "Station pressure at 216 m altitude, not sea level",
              "Sea-level correction with configurable ALTITUDE_M", "Normal readings ≈1008 hPa"],
             ["Runs not reproducible", "Seeds came from Python's hash(), randomised per process",
              "Seeds from zlib.crc32(node_id)", "Identical traces every run; retraining gives identical models"],
             ["Satellite storms never 'cold' enough", "IR mapping left cloud tops above 220 K",
              "IR = 300 − 105·cloud^0.6; stronger overcast core", "Cold cover rises with intensity; flag at ≥0.85"],
             ["ESP32 toolchain could not be downloaded", "Network policy blocked Arduino/Espressif servers",
              "Syntax-checked sketches against stub headers", "No syntax errors; real build planned on lab PC"],
             ["LSTM gave no gain for wind", "Wind gusts are close to random; a straight line is near-optimal",
              "Kept result honest; LSTM used where it helps (pressure, real time)", "Reported as limitation"]],
            [3.3, 4.5, 4.2, 4.0], "Failures and fixes in my modules")

    d.h("Live Demonstration")
    d.numbered(["`python sensor_node.py --node BUOY_07 --loss 0.15 --burst 0.6 --truth-log t.csv` — show LOST lines.",
                "`python satellite_station.py --save-frames frames/` — show raw MB vs bytes sent and saved PNGs.",
                "`python run_demo.py` — yellow dots on the dashboard are my reconstructions; compare with the truth CSV.",
                "Hardware: ESP32 node sends live BMP280 data; turning the knob / pressing BOOT triggers CRITICAL and the "
                "alert LED + buzzer. *(Shown if the breadboard build is complete by the review.)*",
                "`python train_models.py` — dataset sizes and training in ≈20 s."])
    video_plan(d, "sreehari")

    d.h("Feasibility (Five Dimensions)")
    d.table([["Dimension", "Evidence"],
             ["Technical", "Benchmarks in the Section 5 benchmark table met except wind gap repair (equal to baseline) and the pending full firmware build."],
             ["Economic", "Per node: ESP32 ₹350–450 + BMP280 ₹100–150 + knob/reed switch, buzzer, transistor, "
              "breadboard ≈ ₹800; two-node prototype ₹1,600–2,200. Optional LoRa pair ₹800–1,100. Professional "
              "met-ocean buoys cost far more; ours is a low-cost demonstrator, not a replacement."],
             ["Social", "Low cost makes dense coastal networks affordable for local bodies and colleges; feedback to be recorded: ____________"],
             ["Environmental", "ESP32 with Wi-Fi draws on the order of 0.5 W when active; deep sleep and LoRa can cut "
              "this sharply; solar + 18650 option; boards are reusable."],
             ["Operational / Safety", "3.3 V electronics only; LoRa used in India's licence-free 865–867 MHz band; "
              "antenna always attached; sealed enclosure if floated in water."]],
            [3.2, 13.8], "Feasibility with emphasis on my modules")

    d.h("Comparison with Literature")
    d.table([["Parameter", "Existing work", "Our project", "Improved?"],
             ["When repair happens", f"Offline, full series (BRITS) {rf('brits')}", "Online: at gap close and in real time", "Yes"],
             ["Model weight", f"Framework RNNs (GRU-D) {rf('grud')}", "numpy LSTM, ≈5.1 k parameters", "Yes"],
             ["Imputation accuracy", f"Learned bidirectional models {rf('brits', 'grud')}", "Forward + anchor; no gain for wind", "No (not proven)"],
             ["Loss realism in testing", f"Burst channel theory {rf('gilbert', 'elliott')}", "Used to generate test traffic with ground truth", "Applied"],
             ["Radio link", f"LoRa long range at low data rate {rf('lora')}", "Compact 30-byte CSV payload; not yet field-tested", "Not yet"]],
            [3.4, 5.2, 5.6, 2.8], "Comparison with five papers from the Review 1 survey")

    d.h("Scalability and Next Steps")
    d.bullets(["Assemble and field-test 2–3 ESP32 nodes (Wi-Fi first, then LoRa) and measure real loss and battery life.",
               "Train the LSTM on archived buoy data (INCOIS / NOAA NDBC) instead of simulated traces.",
               "Add a bidirectional model for gap repair to try to beat linear interpolation on wind.",
               "Weatherproof enclosure, solar charging and over-the-air firmware updates for deployment."])

    progress(d, "sreehari")
    my_contribution(d, name, "sreehari")
    d.h("Viva Preparation")
    viva(d, [("Why simulate bursty loss instead of random loss?", "Real marine links lose packets in clusters (rain "
              "fade); random loss would make recovery look easier than it is."),
             ("Why anchor the LSTM forecast?", "So estimates join the reading that did arrive without a jump."),
             ("Are the satellite images AI-generated?", "No, they are formula-based (procedural) and fully controllable."),
             ("Why sea-level correction?", "Inland station pressure is lower; without it every reading looks cyclonic."),
             ("What if the gap is longer than 30 readings?", "It is not reconstructed; guessing that far ahead is unreliable.")])
    d.h("Conclusion")
    d.p("The sensing layer I built produces realistic data and realistic loss, records the truth so recovery can be "
        "measured, and runs on affordable hardware. The reconstruction keeps the pressure trend continuous through "
        "real losses and gives immediate estimates while packets are overdue. Field testing of the hardware and "
        "training on real buoy data are the next steps.")
    rf.write(d)
    appendices(d, "sreehari")
    return d, "24BDS0417_Sreehari_R3_Report"


# ============================================================================ shared sections
TESTS = {
    "test_cyclone_raises_wind_and_drops_pressure": "Storm model: wind exceeds 60 km/h and pressure falls below 990 hPa only during the storm",
    "test_priority_beats_fifo_for_critical_under_congestion": "Critical worst-case wait < 0.5 s with QoS, > 0.5 s with FIFO, at 2x overload",
    "test_alert_sheds_non_essential_only_when_congested": "Housekeeping is kept on an idle link and shed only with a backlog",
    "test_next_ready_in_is_consistent_with_dequeue": "Scheduler never reports 'ready' when dequeue would refuse (no busy loop)",
    "test_server_reconstructs_gap": "A 3-packet gap is filled with 3 flagged estimates in sequence order",
    "test_server_late_packet_replaces_estimate": "A late packet replaces its estimate; a repeat is a duplicate",
    "test_server_realtime_concealment_then_repair": "Overdue node gets a provisional forecast, later replaced by gap repair",
    "test_server_node_reboot_starts_fresh_stream": "Sequence restarting at 1 resets the node instead of being discarded",
    "test_predict_fuses_satellite_and_raises_alert": "Satellite risk 90 raises the fused alert; bandwidth metric = 99.95 %",
    "test_api_endpoints": "/health, /predict, /telemetry, /metrics, /snapshot, / and the WebSocket respond correctly",
    "test_satellite_features_track_intensity_and_compress": "Calm frame risk < 10, mature storm > 60 and flagged; record < 1 % of frame",
    "test_qos_classifier_learns_simple_rule": "Logistic regression reaches > 95 % accuracy on a separable rule",
    "test_lstm_gradients_match_numerical": "Backpropagation-through-time gradients equal numerical gradients",
    "test_lstm_learns_a_sine_wave": "LSTM learns a sine wave to MSE < 0.01",
    "test_gateway_classifies_and_drops_invalid": "Malformed / out-of-range packets dropped and counted; wind 80 km/h → CRITICAL + alert",
    "test_gateway_ml_policy_flags_early": "Falling pressure / rising wind flagged CRITICAL before thresholds are crossed",
    "test_gilbert_elliott_mean_loss": "Bursty channel's long-run loss within 8–12 % for a 10 % target",
    "test_reconstruction_fills_gap_and_hits_anchor": "Gap estimates have the right shape and stay close to the trend",
    "test_esp32_json_is_accepted_by_gateway": "The ESP32 firmware's exact JSON packets pass validation and classification",
    "test_lora_serial_bridge_parsing": "LoRa CSV lines convert to valid telemetry; status and garbage lines are ignored",
}

PROGRESS = {
    "laksh": [["Central server", "UDP listener, linear interpolation, /predict, polling HTML table",
               "LSTM gap repair, real-time concealment, late/duplicate/reboot handling, risk fusion + forecast, feedback loop, 9 endpoints + WebSocket"],
              ["QoS", "Priority queue + fixed 0.5 s sleep for NORMAL", "Token-bucket scheduler, 3 classes, critical reserve, congestion-gated shedding, FIFO baseline"],
              ["Data / demo", "Random-walk sensor values; 3 terminals started by hand", "Physics-based cyclone model; one-command launcher; 28 automated tests"]],
    "anvay": [["Classification", "Threshold rule only (2 classes)", "Rule + logistic-regression trend classifier (hybrid), 3 classes, validation"],
              ["Edge AI", "Not started", "Satellite feature extraction, risk score, thumbnail; 99.95 % bandwidth saving"],
              ["Learning / evidence", "No model; 12-second smoke test", "numpy LSTM with BPTT + Adam; evaluation harness with 4 experiments; trained models"]],
    "sreehari": [["Sensor node", "Random losses, random-walk values", "Cyclone physics, bursty Gilbert–Elliott loss, housekeeping, ground-truth log"],
                 ["Satellite station", "Not started", "4-band 16-bit frame synthesis, storm life cycle, feature-only transmission"],
                 ["Recovery / hardware", "Linear interpolation; no hardware", "Anchored LSTM repair + real-time forecast; training pipeline; ESP32 + LoRa firmware, BOM"]],
}

VIDEO = {
    "laksh": ["Live demo: `run_demo.py`, dashboard from calm to alert (continuous, no cuts)",
              "Test results: QoS table and latency chart, live-run counters, failures fixed (busy loop, 50 % cap)",
              "Comparison with DiffServ / RED / DRR / edge papers (Section 8)",
              "My contribution (server, scheduler, dashboard, tests) and scalability plan"],
    "anvay": ["Live demo: gateway log + dashboard ML column during a run; satellite panel",
              "Test results: classifier lead time, LSTM training curve and gradient check, fixes",
              "Comparison with Dvorak / ADT / CNN / GRU-D (Section 8)",
              "My contribution (edge AI, gateway, LSTM, evaluation) and next steps"],
    "sreehari": ["Live demo: sensor LOST lines → yellow dots; satellite frames; ESP32 node if built",
                 "Test results: reconstruction MAE table, live-run truth vs estimate, fixes",
                 "Comparison with BRITS / GRU-D / Gilbert–Elliott / LoRa (Section 8)",
                 "My contribution (sensing layer, hardware, reconstruction) and field-test plan"],
}

RUN = {
    "laksh": [["`python run_demo.py`", "Starts everything; dashboard at http://127.0.0.1:8000"],
              ["`python run_demo.py --duration 90`", "Headless run, prints final /metrics and gateway stats"],
              ["`python run_demo.py --scheduler fifo --backbone-bps 1000`", "Baseline without QoS on a tight link"],
              ["`uvicorn central_server:app --port 8000`", "Server only (RECON_METHOD=linear for baseline)"],
              ["`python -m pytest -q`", "Runs the 28 automated tests"]],
    "anvay": [["`python edge_gateway.py --policy hybrid`", "Gateway with rule + ML (also: rule, ml)"],
              ["`python edge_gateway.py --scheduler fifo --backbone-bps 1000`", "Gateway baseline, tight link"],
              ["`python train_models.py`", "Retrains LSTM and classifier (≈20 s)"],
              ["`python evaluate.py`", "Reproduces results/REPORT.md and plots"],
              ["`curl 127.0.0.1:8000/gateway`", "Live gateway QoS statistics"]],
    "sreehari": [["`python sensor_node.py --node BUOY_07 --loss 0.15 --burst 0.6 --truth-log t.csv`", "Bursty-loss node with ground truth"],
                 ["`python satellite_station.py --save-frames frames/`", "Ground station; writes IR previews"],
                 ["`python run_demo.py --no-sensors`", "Server + gateway only, for ESP32 nodes"],
                 ["`python hardware/serial_bridge.py --port COM3`", "LoRa receiver → gateway"],
                 ["`python train_models.py --quick`", "Fast training run for testing"]],
}


def progress(d, key):
    d.h("Progress since Review 2")
    d.table([["Area", "At Review 2 (14/9)", "Now (Review 3)"]] + PROGRESS[key], [3.0, 5.6, 8.4],
            "What changed in my modules between reviews")
    d.p("Overall completion: software 100 % of planned scope (all modules running and tested); "
        + ("hardware firmware complete, physical node build in progress; " if key == "sreehari" else "")
        + "validation on real buoy data not yet started.")


def video_plan(d, key):
    d.h("Review 3 Video Plan (6 minutes)", 2)
    mins = ["0:00–2:00", "2:00–4:00", "4:00–5:00", "5:00–6:00"]
    d.table([["Time", "Content"]] + [[m, v] for m, v in zip(mins, VIDEO[key])], [2.6, 14.4])
    d.p("The video starts with my name, register number, team number and project title, as required.")


def appendices(d, key):
    d.page_break()
    d.h("Appendix A — How to Run My Modules", 1, numbered=False)
    d.table([["Command", "Purpose"]] + RUN[key], [8.5, 8.5])
    d.h("Appendix B — Evidence from the Live Run (12/10/2026)", 1, numbered=False)
    d.p("Unedited excerpts from the log files produced by `python run_demo.py --duration 75`:", "Body")
    d.code(log_excerpt(key))


def _grep(path, pattern, n):
    import re as _re
    out = []
    for line in open(path, errors="replace"):
        if _re.search(pattern, line):
            out.append(line.rstrip()[:110])
            if len(out) >= n:
                break
    return out


def log_excerpt(key):
    L = os.path.join(REPO, "logs")
    E = os.path.join(HERE, "evidence")
    if key == "laksh":
        return (["# live_run_output.txt (status printed by run_demo.py every 5 s)"] +
                _grep(os.path.join(E, "live_run_output.txt"), r"^\[\s*\d+s\]", 15) +
                ["# logs/server.log"] + _grep(os.path.join(L, "server.log"), r"reconstructed|late_recovered|listening", 8))
    if key == "anvay":
        return (["# logs/gateway.log"] + _grep(os.path.join(L, "gateway.log"), r"listening|alert", 3) +
                _grep(os.path.join(L, "gateway.log"), r"CRITICAL .* forwarded", 5) +
                _grep(os.path.join(L, "gateway.log"), r"shed", 3) +
                ["# train_log.txt"] + _grep(os.path.join(E, "train_log.txt"), r"LSTM|QoS classifier|epoch +(1|20)/", 8))
    return (["# logs/buoy_07.log"] + _grep(os.path.join(L, "buoy_07.log"), r"started|LOST", 6) +
            ["# logs/satellite.log"] + _grep(os.path.join(L, "satellite.log"), r"frame 000[1-2]|flag=True", 4) +
            ["# logs/truth_BUOY_07.csv (lost=1 rows are what the server had to reconstruct)"] +
            [ln.strip() for ln in open(os.path.join(L, "truth_BUOY_07.csv"))][:1] +
            [ln.strip() for ln in open(os.path.join(L, "truth_BUOY_07.csv")) if ln.strip().endswith(",1")][:6])


CONTRIB = {
    "laksh": dict(
        mine=["Central prediction server (central_server.py): ingest, gap/late/reboot handling, concealment, fusion, feedback, API",
              "Live dashboard (dashboard.html) with WebSocket and polling fallback",
              "QoS scheduler (qos.py): token bucket, strict priority, critical reserve, shedding",
              "Cyclone/ocean physics and loss channel (ocean_model.py)",
              "One-command launcher (run_demo.py) and the 28-test suite (tests/)"],
        tests="test_cyclone_raises_wind_and_drops_pressure, test_priority_beats_fifo_for_critical_under_congestion, "
              "test_alert_sheds_non_essential_only_when_congested, test_next_ready_in_is_consistent_with_dequeue, "
              "test_server_reconstructs_gap, test_server_late_packet_replaces_estimate, "
              "test_server_realtime_concealment_then_repair, test_server_node_reboot_starts_fresh_stream, "
              "test_predict_fuses_satellite_and_raises_alert, test_api_endpoints",
        logs="logs/server.log (reconstruction lines), live_run_output.txt (status every 5 s, final /metrics)"),
    "anvay": dict(
        mine=["Edge AI (edge_ai.py): satellite feature extraction, risk score, ML trend classifier",
              "Edge gateway (edge_gateway.py): validation, hybrid classification, alerts, feedback, node notifications",
              "LSTM from scratch (lstm.py) with BPTT and Adam",
              "Evaluation harness (evaluate.py) → results/REPORT.md and plots",
              "Trained models (models/) and run logs (logs/)"],
        tests="test_satellite_features_track_intensity_and_compress, test_qos_classifier_learns_simple_rule, "
              "test_lstm_gradients_match_numerical, test_lstm_learns_a_sine_wave, test_gateway_classifies_and_drops_invalid, "
              "test_gateway_ml_policy_flags_early",
        logs="logs/gateway.log (classification, 'alert ACTIVE', reserve lines), results/results.json, train_log.txt"),
    "sreehari": dict(
        mine=["Hardware: ESP32 buoy firmware, LoRa buoy/receiver sketches, serial bridge, hardware guide and BOM",
              "Lost-telemetry reconstruction (reconstruction.py): anchored gap repair and real-time forecast",
              "Satellite ground station (satellite_station.py): 4-band frame synthesis and byte accounting",
              "Sensor-node simulator (sensor_node.py): readings, bursty loss, housekeeping, truth log",
              "Training pipeline (train_models.py)"],
        tests="test_gilbert_elliott_mean_loss, test_reconstruction_fills_gap_and_hits_anchor, "
              "test_esp32_json_is_accepted_by_gateway, test_lora_serial_bridge_parsing",
        logs="logs/buoy_07.log (LOST lines), logs/satellite.log (MB → bytes), logs/truth_*.csv, train_log.txt"),
}
OWNER = {"laksh": "Laksh Ahuja", "anvay": "Anvay Sharma", "sreehari": "Sreehari"}


def my_contribution(d, name, key):
    d.h("My Contribution")
    rows = [["Tasks I did", "Tasks done by teammates"]]
    others = [k for k in CONTRIB if k != key]
    theirs = [f"{OWNER[k]}: " + "; ".join(x.split(" (")[0] for x in CONTRIB[k]["mine"][:3]) for k in others]
    mine = CONTRIB[key]["mine"]
    for i in range(max(len(mine), 2)):
        rows.append([mine[i] if i < len(mine) else "", theirs[i] if i < len(theirs) else ""])
    d.table(rows, [8.5, 8.5], "Division of work")
    d.p("**Evidence of my work:**")
    d.bullets([f"Code: the files listed in my Implementation section ({REPO_URL}).",
               "Automated tests covering my modules, all passing (Table below; full output in "
               "`docs/reports/evidence/pytest_output.txt`).",
               f"Run logs from the live demonstration: {CONTRIB[key]['logs']} (excerpts in Appendix B).",
               "Figures in this report generated from those logs by `docs/reports/make_figures.py`."])
    d.table([["Automated test (tests/test_pipeline.py)", "What it checks", "Result"]] +
            [[t, TESTS[t], "PASSED"] for t in CONTRIB[key]["tests"].split(", ")],
            [6.4, 8.6, 2.0], "Tests covering my modules")
    d.note("[Insert here: screenshot of my own commits / work session and a photo of me testing — required by the "
           "rubric. Shared files (common.py, mininet_topology.py) were developed jointly.]")


def viva(d, qa):
    for q, a in qa:
        d.p(f"**Q: {q}** {a}", "Bullet")


def convert(fodt, outdir):
    for fmt in ("odt", "pdf"):
        subprocess.run(["soffice", "--headless", "--convert-to", fmt, "--outdir", outdir, fodt],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn in (laksh, anvay, sreehari):
        doc, base = fn()
        path = os.path.join(OUT, base + ".fodt")
        doc.save(path)
        convert(path, OUT)
        os.remove(path)
        print("built", base)
