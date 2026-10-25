"""Individual Review-1 and Review-2 reports (PDF + ODT) for all three team members.

Run from the repository root:
    python docs/reports/make_r1r2_figures.py
    python docs/reports/build_r1r2.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from build_reports import REFS, REPO_URL, TEAM, TITLE, Refs  # noqa: E402
from odt import Doc  # noqa: E402

OUT = os.path.join(HERE, "out")
RF = os.path.join(HERE, "fig")
AS = os.path.join(HERE, "assets")

REFS.update({
    "mao": 'Y. Mao, C. You, J. Zhang, K. Huang, and K. B. Letaief, "A survey on mobile edge computing: The communication perspective," *IEEE Communications Surveys & Tutorials*, vol. 19, no. 4, pp. 2322–2358, 2017.',
    "alfuqaha": 'A. Al-Fuqaha, M. Guizani, M. Mohammadi, M. Aledhari, and M. Ayyash, "Internet of Things: A survey on enabling technologies, protocols, and applications," *IEEE Communications Surveys & Tutorials*, vol. 17, no. 4, pp. 2347–2376, 2015.',
    "xu": 'G. Xu, Y. Shi, X. Sun, and W. Shen, "Internet of Things in marine environment monitoring: A review," *Sensors*, vol. 19, no. 7, art. 1711, 2019.',
    "raza": 'U. Raza, P. Kulkarni, and M. Sooriyabandara, "Low power wide area networks: An overview," *IEEE Communications Surveys & Tutorials*, vol. 19, no. 2, pp. 855–873, 2017.',
    "chenr": 'R. Chen, W. Zhang, and X. Wang, "Machine learning in tropical cyclone forecast modeling: A review," *Atmosphere*, vol. 11, no. 7, art. 676, 2020.',
    "chenb": 'B.-F. Chen, B. Chen, H.-T. Lin, and R. L. Elsberry, "Estimating tropical cyclone intensity by satellite imagery utilizing convolutional neural networks," *Weather and Forecasting*, vol. 34, no. 2, pp. 447–465, 2019.',
    "denby": 'B. Denby and B. Lucia, "Orbital edge computing: Nanosatellite constellations as a new class of computer system," in *Proc. ACM ASPLOS*, 2020.',
    "phisat": 'G. Giuffrida *et al.*, "The Φ-Sat-1 mission: The first on-board deep neural network demonstrator for satellite Earth observation," *IEEE Trans. Geoscience and Remote Sensing*, vol. 60, 2022.',
    "gain": 'J. Yoon, J. Jordon, and M. van der Schaar, "GAIN: Missing data imputation using generative adversarial nets," in *Proc. ICML*, 2018.',
    "limz": 'B. Lim and S. Zohren, "Time-series forecasting with deep learning: A survey," *Philosophical Transactions of the Royal Society A*, vol. 379, art. 20200209, 2021.',
    "bonomi": 'F. Bonomi, R. Milito, J. Zhu, and S. Addepalli, "Fog computing and its role in the Internet of Things," in *Proc. MCC Workshop on Mobile Cloud Computing*, 2012, pp. 13–16.',
    "xgb": 'T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. ACM KDD*, 2016, pp. 785–794.',
    "jouhari": 'M. Jouhari, K. Ibrahimi, H. Tembine, and J. Ben-Othman, "Underwater wireless sensor networks: A survey on enabling technologies, localization protocols, and Internet of Underwater Things," *IEEE Access*, vol. 7, pp. 96879–96899, 2019.',
    # recent literature (2018 onwards) used in the R1 survey tables
    "yu18": 'W. Yu, F. Liang, X. He, W. G. Hatcher, C. Lu, J. Lin, and X. Yang, "A survey on the edge computing for the Internet of Things," *IEEE Access*, vol. 6, pp. 6900–6919, 2018.',
    "abbas18": 'N. Abbas, Y. Zhang, A. Taherkordi, and T. Skeie, "Mobile edge computing: A survey," *IEEE Internet of Things Journal*, vol. 5, no. 1, pp. 450–465, 2018.',
    "hassan18": 'N. Hassan, S. Gillani, E. Ahmed, I. Yaqoob, and M. Imran, "The role of edge computing in Internet of Things," *IEEE Communications Magazine*, vol. 56, no. 11, pp. 110–115, 2018.',
    "pham20": 'Q.-V. Pham, F. Fang, V. N. Ha, M. J. Piran, M. Le, L. B. Le, W.-J. Hwang, and Z. Ding, "A survey of multi-access edge computing in 5G and beyond: Fundamentals, technology integration, and state-of-the-art," *IEEE Access*, vol. 8, pp. 116974–117017, 2020.',
    "zhou19": 'Z. Zhou, X. Chen, E. Li, L. Zeng, K. Luo, and J. Zhang, "Edge intelligence: Paving the last mile of artificial intelligence with edge computing," *Proceedings of the IEEE*, vol. 107, no. 8, pp. 1738–1762, 2019.',
    "esposito22": 'M. Esposito, L. Palma, A. Belli, L. Sabbatini, and P. Pierleoni, "Recent advances in Internet of Things solutions for early warning systems: A review," *Sensors*, vol. 22, no. 6, art. 2124, 2022.',
    "centenaro21": 'M. Centenaro, C. E. Costa, F. Granelli, C. Sacchi, and L. Vangelista, "A survey on technologies, standards and open challenges in satellite IoT," *IEEE Communications Surveys & Tutorials*, vol. 23, no. 3, pp. 1693–1720, 2021.',
    "kodheli21": 'O. Kodheli *et al.*, "Satellite communications in the new space era: A survey and future challenges," *IEEE Communications Surveys & Tutorials*, vol. 23, no. 1, pp. 70–109, 2021.',
    "bennis18": 'M. Bennis, M. Debbah, and H. V. Poor, "Ultrareliable and low-latency wireless communication: Tail, risk, and scale," *Proceedings of the IEEE*, vol. 106, no. 10, pp. 1834–1853, 2018.',
    "popovski18": 'P. Popovski, J. J. Nielsen, C. Stefanovic, E. de Carvalho, E. Ström, K. F. Trillingsgaard, A.-S. Bana, D. M. Kim, R. Kotaba, J. Park, and R. B. Sørensen, "Wireless access for ultra-reliable low-latency communication: Principles and building blocks," *IEEE Network*, vol. 32, no. 2, pp. 16–23, 2018.',
    "yates21": 'R. D. Yates, Y. Sun, D. R. Brown, S. K. Kaul, E. Modiano, and S. Ulukus, "Age of information: An introduction and survey," *IEEE Journal on Selected Areas in Communications*, vol. 39, no. 5, pp. 1183–1210, 2021.',
    "fuller20": 'A. Fuller, Z. Fan, C. Day, and C. Barlow, "Digital twin: Enabling technologies, challenges and open research," *IEEE Access*, vol. 8, pp. 108952–108971, 2020.',
    "chavas22": 'D. R. Chavas and J. A. Knaff, "A simple model for predicting the tropical cyclone radius of maximum wind from outer size," *Weather and Forecasting*, vol. 37, no. 5, pp. 563–579, 2022.',
    "adt19": 'T. L. Olander and C. S. Velden, "The Advanced Dvorak Technique (ADT) for estimating tropical cyclone intensity: Update and new capabilities," *Weather and Forecasting*, vol. 34, no. 4, pp. 905–922, 2019.',
    "wimmers19": 'A. Wimmers, C. Velden, and J. H. Cossuth, "Using deep learning to estimate tropical cyclone intensity from satellite passive microwave imagery," *Monthly Weather Review*, vol. 147, no. 6, pp. 2261–2282, 2019.',
    "ruttgers19": 'M. Rüttgers, S. Lee, S. Jeon, and D. You, "Prediction of a typhoon track using a generative adversarial network and satellite images," *Scientific Reports*, vol. 9, art. 6057, 2019.',
    "chenran19": 'J. Chen and X. Ran, "Deep learning with edge computing: A review," *Proceedings of the IEEE*, vol. 107, no. 8, pp. 1655–1674, 2019.',
    "wang20": 'X. Wang, Y. Han, V. C. M. Leung, D. Niyato, X. Yan, and X. Chen, "Convergence of edge computing and deep learning: A comprehensive survey," *IEEE Communications Surveys & Tutorials*, vol. 22, no. 2, pp. 869–904, 2020.',
    "ray22": 'P. P. Ray, "A review on TinyML: State-of-the-art and prospects," *Journal of King Saud University – Computer and Information Sciences*, vol. 34, no. 4, pp. 1595–1623, 2022.',
    "banbury21": 'C. Banbury *et al.*, "MLPerf Tiny benchmark," in *Proc. NeurIPS Datasets and Benchmarks Track*, 2021.',
    "vanhoudt20": 'G. Van Houdt, C. Mosquera, and G. Nápoles, "A review on the long short-term memory model," *Artificial Intelligence Review*, vol. 53, no. 8, pp. 5929–5955, 2020.',
    "rudin19": 'C. Rudin, "Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead," *Nature Machine Intelligence*, vol. 1, pp. 206–215, 2019.',
    "grinsztajn22": 'L. Grinsztajn, E. Oyallon, and G. Varoquaux, "Why do tree-based models still outperform deep learning on typical tabular data?" in *Proc. NeurIPS Datasets and Benchmarks Track*, 2022.',
    "haxhibeqiri18": 'J. Haxhibeqiri, E. De Poorter, I. Moerman, and J. Hoebeke, "A survey of LoRaWAN for IoT: From technology to application," *Sensors*, vol. 18, no. 11, art. 3995, 2018.',
    "mekki19": 'K. Mekki, E. Bajic, F. Chaxel, and F. Meyer, "A comparative study of LPWAN technologies for large-scale IoT deployment," *ICT Express*, vol. 5, no. 1, pp. 1–7, 2019.',
    "parri21": 'L. Parri, S. Parrino, G. Peruzzi, and A. Pozzebon, "Offshore LoRaWAN networking: Transmission performances analysis under different environmental conditions," *IEEE Trans. Instrumentation and Measurement*, vol. 70, 2021.',
    "babiuch19": 'M. Babiuch, P. Foltýnek, and P. Smutný, "Using the ESP32 microcontroller for data processing," in *Proc. 20th Int. Carpathian Control Conference (ICCC)*, 2019, pp. 1–6.',
    "csdi21": 'Y. Tashiro, J. Song, Y. Song, and S. Ermon, "CSDI: Conditional score-based diffusion models for probabilistic time series imputation," in *Proc. NeurIPS*, 2021.',
    "saits23": 'W. Du, D. Cote, and Y. Liu, "SAITS: Self-attention-based imputation for time series," *Expert Systems with Applications*, vol. 219, art. 119619, 2023.',
})

ROLES = {
    "laksh": [["Member", "Role", "How their work meets mine"],
              ["Laksh Ahuja (24BDS0212) — me", "Central server, dashboard & network QoS",
               "I own everything after the gateway: link scheduling, the prediction server and its API, the "
               "dashboard, the cyclone scenario used in demos, and the automated tests"],
              ["Anvay Sharma (24BCE0824)", "Edge gateway & edge intelligence",
               "His gateway labels each packet; my scheduler and server trust that label, so we agree the class "
               "names and thresholds together"],
              ["Sreehari (24BDS0417)", "Sensing layer, hardware & data recovery",
               "His nodes produce the sequence numbers my server checks, and his gap-filling function runs "
               "inside my server"]],
    "anvay": [["Member", "Responsibility", "Interface with the gateway (my module)"],
              ["Anvay Sharma (24BCE0824) — me", "Edge gateway, classification, satellite analysis, ML models",
               "Receive, check and label every packet; decide what leaves the edge first; shrink satellite data"],
              ["Sreehari (24BDS0417)", "Sensor and satellite simulators, hardware nodes, gap recovery",
               "Upstream of me: sends JSON readings to my UDP port 9001"],
              ["Laksh Ahuja (24BDS0212)", "Prediction server, dashboard, link QoS, testing",
               "Downstream of me: my forwarder sends to his server on UDP port 9002"]],
    "sreehari": [["Team member", "Area", "What I hand over / receive"],
                 ["Sreehari (24BDS0417) — me", "Sensors, satellite station, ESP32 nodes, recovery of lost readings",
                  "I define the reading format and the loss behaviour, and supply the gap-filling method"],
                 ["Anvay Sharma (24BCE0824)", "Gateway and edge AI",
                  "Receives my packets first; needs my thresholds-crossing scenarios to test his classifier"],
                 ["Laksh Ahuja (24BDS0212)", "Server, dashboard, QoS",
                  "Calls my reconstruction code when his server sees a missing sequence number"]],
}


def cover(d, name, reg, review, date, role, summary):
    d.spacer()
    d.p("INDIVIDUAL PROJECT REPORT", "Center")
    d.p(f"{review} ({date})", "Center")
    d.spacer()
    d.p(TITLE, "Title")
    d.spacer()
    d.table([["Student", "Register No.", "Team No.", "My role"], [name, reg, "________", role]], [3.6, 3.0, 2.2, 8.2])
    d.p(f"**Team:** {', '.join(f'{n} ({r})' for n, r in TEAM)}.  **Repository:** {REPO_URL}")
    d.h("Summary", 1, numbered=False)
    d.p(summary)
    d.page_break()


def evidence_table(d, rows):
    d.table([["Source", "Published fact / figure", "Why it matters for my part"]] + rows, [4.0, 6.5, 6.5],
            "Evidence that the problem is real")


def timeline(d, weeks):
    d.table([["Week", "Dates", "My milestone", "Deliverable / check"]] + weeks, [1.6, 2.8, 7.2, 5.4],
            "My weekly plan from Review 1 to Review 2")


PLACEHOLDER = {
    "laksh": "[Insert: dated screenshot of my terminal running central_server.py with /predict open in the browser, "
             "and my GitHub commit list. Our early commits went through one shared account, so the file split above "
             "is the record of who wrote what.]",
    "anvay": "[Insert: dated screenshot of edge_gateway.py printing CRITICAL / NORMAL lines while I test it, plus a "
             "photo of me at the laptop during the test. Commits from my own GitHub account will be added from R3.]",
    "sreehari": "[Insert: dated screenshot of three sensor_node.py terminals showing LOST lines, and the hardware "
                "parts list or shop quotation. My later commits will be pushed from my own GitHub account.]",
}


def contrib_placeholder(d, who):
    d.note(PLACEHOLDER[who])


# ============================================================================ extra per-person sections
OBJ = {
    "laksh": [["Server keeps a per-node history and detects every missing sequence number", "100 % of gaps detected in test runs"],
              ["Fused cyclone-risk output and alert available through an API", "/predict answers in < 1 s; alert at risk ≥ 60"],
              ["Critical readings forwarded ahead of routine traffic on a slow link", "Critical latency well below normal traffic under load"],
              ["Live dashboard that shows estimated vs measured data", "Updates at least every 2 s"],
              ["Network topology emulated with routing", "End-to-end ping buoy → server succeeds"]],
    "anvay": [["Classify every packet at the gateway as CRITICAL or NORMAL", "No breach of 60 km/h / 990 hPa missed"],
              ["Warn before thresholds are crossed using the trend of readings", "Positive lead time in test scenarios"],
              ["Cut satellite data sent over the backbone", "> 95 % fewer bytes than the raw frame"],
              ["Gateway that never crashes on bad input", "Malformed packets counted and dropped"],
              ["Fair, repeatable evaluation of every model", "Held-out scenarios and a simple baseline for each"]],
    "sreehari": [["Realistic sensor readings with a storm that arrives and passes", "Wind > 60 km/h and pressure < 990 hPa only during the storm"],
                 ["Packet loss that matches real marine links", "Configurable loss rate; bursts of consecutive losses"],
                 ["Record the true value of every reading, even lost ones", "Ground-truth file for every test run"],
                 ["Recover lost readings better than simple methods", "Lower error than holding the last value"],
                 ["Low-cost hardware node sending the same message format", "≤ ₹1,000 per node"]],
}

APPROACH = {
    "laksh": [("Central server", "Python FastAPI service with a background UDP listener; per-node ring buffer of recent "
               "readings; sequence-number tracking to detect gaps; risk score from wind and pressure; REST endpoints."),
              ("Dashboard", "Single HTML page that polls the API and highlights CRITICAL nodes and estimated values."),
              ("QoS on the slow link", "Start with a priority queue (critical first); later model the link capacity "
               "explicitly so that urgent data never waits behind routine data."),
              ("Simulation and testing", "A cyclone scenario for the sensors, Packet Tracer for routing, and scripted "
               "end-to-end runs so every result can be repeated.")],
    "anvay": [("Gateway", "Two threads — receiver and forwarder — joined by a priority queue; threshold rule first so the "
               "pipeline can be verified."),
              ("Early warning", "Features from the last few readings (pressure falling, wind rising, distance to the "
               "thresholds) fed to a small, explainable classifier."),
              ("Satellite images", "Extract the cues forecasters use — cold cloud tops, symmetry, an eye — at the ground "
               "station and send only those numbers."),
              ("Evaluation", "Compare every model with a simple baseline on scenarios it has not seen.")],
    "sreehari": [("Sensor simulator", "One reading per second with a sequence number, compact JSON over UDP, and a "
                  "configurable loss probability."),
                 ("Storm and loss models", "Begin with a ramp, then a physical wind/pressure profile; begin with random "
                  "loss, then a burst-loss channel."),
                 ("Recovery of lost readings", "Linear interpolation as the baseline, then a learned time-series model "
                  "evaluated against recorded ground truth."),
                 ("Hardware", "ESP32 with a BMP280 pressure/temperature sensor sending the same JSON as the simulator.")],
}

RISKS = {
    "laksh": [["Thread timing bugs between listener and API", "Medium", "High", "Start threads in framework hooks; test end to end"],
              ["No real buoy data", "High", "Medium", "Physics-based simulation; real archives later"],
              ["Packet Tracer cannot run our Python code", "High", "Low", "Use it for routing; run code on loopback / Mininet"],
              ["Scope creep before Review 2", "Medium", "Medium", "Weekly milestones; baseline first"]],
    "anvay": [["No labelled satellite images", "High", "High", "Synthetic frames with known storm intensity"],
              ["ML classifier raises false alarms", "Medium", "Medium", "Keep the threshold rule as a safety floor"],
              ["Deep-learning frameworks too heavy for the edge", "Medium", "Medium", "Prefer small NumPy models"],
              ["Gateway crashes on bad packets", "Medium", "High", "Validate every packet before use"]],
    "sreehari": [["Hardware parts delayed or faulty", "Medium", "Medium", "Software simulator first; borrow from lab"],
                 ["Simulated data too unrealistic", "Medium", "High", "Use published storm profiles and burst-loss models"],
                 ["Recovery no better than interpolation", "Medium", "Medium", "Report honestly; keep interpolation as fallback"],
                 ["Pressure reads wrong indoors (altitude)", "High", "Medium", "Convert station pressure to sea level"]],
}

RUNS = {
    "laksh": [["Team test, 12 s, 2 nodes", "Server + gateway + BUOY_07, RADAR_A", "66 packets, 11 reconstructed, 2 critical; risk 100, alert on"],
              ["Startup test", "Sensors started before the listener", "/predict empty → fixed with startup event"],
              ["Re-run, 60 s, 3 nodes", "Prototype commit 82bcb8a", "160 received, 22 reconstructed, 42 critical; alert at ≈30 s"],
              ["Robustness test", "One non-JSON datagram to port 9002", "Listener thread died; /status stayed at 0 received"],
              ["Packet Tracer", "ping BUOY-01 → 10.40.40.10", "Successful end to end over OSPF"]],
    "anvay": [["Team test, 12 s, 2 nodes", "Gateway between sensors and server", "2 packets classified CRITICAL once wind > 60"],
              ["Re-run, 60 s, 3 nodes", "Prototype commit 82bcb8a", "160 forwarded; 42 CRITICAL sent first; 28 NORMAL throttled"],
              ["Robustness test", "One non-JSON datagram to port 9001", "Receiver thread died; later packets ignored"],
              ["Alert-hold check", "Code review of the forwarder loop", "Alert can be stale after a silent period"]],
    "sreehari": [["Team test, 12 s, 2 nodes", "BUOY_07 (15 % loss), RADAR_A (10 %)", "11 lost packets filled by interpolation"],
                 ["Re-run, 60 s, 3 nodes", "Prototype commit 82bcb8a", "22 packets lost, all 22 reconstructed by the server"],
                 ["Burst analysis", "Runs of LOST lines in the logs", "Longest run 2 packets — losses too scattered"],
                 ["Storm-shape check", "300 simulated steps of the node logic", "Wind fixed at 120, pressure at 930 after ≈100 s"],
                 ["Unit check of reconstruct_gap()", "Gap 10 → 13", "Values correct, timestamps wrong (all 12:00:03)"]],
}

PLAN3 = {
    "laksh": [["15–21 Sep", "Token-bucket QoS scheduler with critical reserve; FIFO baseline for comparison"],
              ["22–28 Sep", "Server hardening: validation, late/duplicate packets, real-time estimates for overdue packets"],
              ["29 Sep–5 Oct", "WebSocket dashboard; physics-based cyclone model; one-command launcher"],
              ["6–9 Oct", "Automated test suite; measurements for the final report"]],
    "anvay": [["15–21 Sep", "Input validation and capacity-based forwarding in the gateway"],
              ["22–28 Sep", "Trend-based ML classifier (logistic regression) with the rule as safety floor"],
              ["29 Sep–5 Oct", "Satellite feature extraction; LSTM implementation in NumPy"],
              ["6–9 Oct", "Evaluation harness, results tables, trained models in the repository"]],
    "sreehari": [["15–21 Sep", "Physics-based storm (approach, pass, recede) and burst-loss channel"],
                 ["22–28 Sep", "Ground-truth logging; satellite-station simulator"],
                 ["29 Sep–5 Oct", "Learned reconstruction model and training pipeline"],
                 ["6–9 Oct", "ESP32 firmware and hardware guide; LoRa option"]],
}

VID1 = ["Problem and evidence (1.5 min)", "Literature gap (1.5 min)", "Proposed solution and feasibility (2 min)",
        "My role and timeline (1 min)"]
VID2 = ["Design walkthrough (2 min)", "Live progress with my own work on screen (2 min)", "One problem and its "
        "solution (1 min)", "Updated cost and my contribution (1 min)"]


def objectives(d, who):
    d.h("Objectives of My Part", 2, numbered=False)
    d.table([["Objective", "Measurable success criterion"]] + OBJ[who], [10.0, 7.0])


def approach(d, who):
    d.h("Planned Method for My Part", 2, numbered=False)
    d.table([["Component", "Planned method"]] + [list(r) for r in APPROACH[who]], [3.6, 13.4])


def risks(d, who):
    d.table([["Risk", "Likelihood", "Impact", "Mitigation"]] + RISKS[who], [5.6, 2.2, 2.0, 7.2], "Risk register for my part")


def video(d, items, review, who):
    d.h(f"{review} Video Plan", 2, numbered=False)
    d.table([["Segment", "What I show"]] + [[a, "Face + screen; " + b] for a, b in zip(items, VIDEO_SHOW[review][who])],
            [6.0, 11.0])


def runs(d, who):
    d.table([["Test run", "Setup", "Observation"]] + RUNS[who], [4.0, 5.4, 7.6], "Test runs performed on my module")


def plan3(d, who):
    d.h("Plan from Review 2 to Review 3", 2, numbered=False)
    d.table([["Week", "Planned work"]] + PLAN3[who], [3.0, 14.0])


VIDEO_SHOW = {
    "R1": {"laksh": ["the IMD coastline / Odisha figures and my 2.1 MB-frame calculation",
                     "my 15-paper table and the gap between network priority and cyclone risk",
                     "the block diagram with my server, dashboard and QoS blocks", "my weekly plan"],
           "anvay": ["the WMO loss figures and why late detection is costly",
                     "papers on satellite intensity estimation and edge AI; the edge gap",
                     "the gateway and edge-analysis blocks I will build", "my three-week gateway plan"],
           "sreehari": ["the offshore LoRaWAN measurements and burst-loss evidence",
                        "imputation and LPWAN papers; why offline imputation is not enough",
                        "the sensing and recovery blocks; the ESP32 cost estimate", "my sensor-to-hardware timeline"]},
    "R2": {"laksh": ["the architecture and my server flowchart", "server + API running, /predict in the browser",
                     "the startup-race fix and the malformed-packet crash", "my cost table and division of work"],
           "anvay": ["the architecture and my gateway flowchart", "gateway log classifying packets live",
                     "the crash on bad input and the 0.5 s throttle problem", "comparison table and division of work"],
           "sreehari": ["the architecture, my sensor flowchart and the circuit diagram",
                        "three nodes running with LOST lines; filled gaps in /status",
                        "scattered losses and the wrong-timestamp bug", "hardware cost table and division of work"]},
}


def finish(d, base):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, base + ".fodt")
    d.save(path)
    for fmt in ("odt", "pdf"):
        subprocess.run(["soffice", "--headless", "--convert-to", fmt, "--outdir", OUT, path], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(path)
    print("built", base)


def newdoc(reg, name, review, fname):
    return Doc(f"{reg} | {name} | {review} Individual Report", f"Individual Project Report | {review}",
               "AI-Driven Edge–Cloud Cyclone Prediction & Network Resilience", fname, TITLE)


# ============================================================================ R1 LAKSH
def r1_laksh():
    name, reg = TEAM[0]
    rf = Refs(["imd", "esposito22", "yu18", "abbas18", "hassan18", "pham20", "zhou19", "xu", "centenaro21",
               "kodheli21", "bennis18", "popovski18", "yates21", "fuller20", "chenr", "chavas22", "holland", "diffserv"])
    d = newdoc(reg, name, "R1", f"{reg}_LakshAhuja_R1")
    cover(d, name, reg, "Review 1 — Problem Identification & Proposal", "24/8/2026",
          "Central server, dashboard, network QoS, cyclone simulation and testing",
          "This report states the problem our team is solving, the evidence that it is real, what earlier work has "
          "tried, and the solution we propose. My own focus is the back half of the system: how cyclone telemetry "
          "should be prioritised on a slow link, and how a central server should turn incomplete data into a "
          "reliable cyclone-risk picture on a live dashboard.")
    d.h("Problem Statement")
    d.p("During a cyclone, ocean buoys and coastal stations must push their readings over slow, unreliable links, so "
        "the most important readings arrive late or not at all — exactly when forecasters and coastal residents "
        "need them most.")
    d.bullets(["**Why it matters:** cyclone warnings save lives only if they are timely; stale or missing pressure "
               "and wind data delays evacuation decisions.",
               "**Who is affected:** coastal and island communities and fishers on India's east coast, and the "
               "district disaster-management officials who order evacuations.",
               "**If unsolved:** a monitoring network treats a routine battery report and a falling-pressure alarm "
               "equally. One 2.1 MB satellite frame occupies a 9.6 kbps backhaul for about **29 minutes**; any alarm "
               "queued behind it waits that long, and gaps from packet loss leave the dashboard blank or wrong during "
               "the critical hours."])
    objectives(d, "laksh")
    d.h("Evidence the Problem is Real")
    evidence_table(d, [
        [f"India Meteorological Department {rf('imd')}", "India has a coastline of about 7,500 km; the 1999 Odisha "
         "super cyclone killed about 10,000 people.", "The people at risk depend on coastal data reaching the "
         "warning centre on time."],
        [f"Esposito et al., 2022 {rf('esposito22')}", "Review of IoT early-warning systems: finds gaps in the "
         "literature and recommends adding a fog/edge layer to warning architectures.", "Supports making decisions "
         "near the data while a central server keeps the overall picture."],
        ["Engineering estimate (our calculation)", "4 bands × 512 × 512 pixels × 2 bytes = 2,097,152 bytes; at "
         "9,600 bit/s: 2,097,152 × 8 / 9,600 ≈ 1,748 s ≈ 29 min.", "Shows why the link must decide what to send "
         "first — the core of my QoS work."]])
    d.h("Literature Survey")
    d.table([["#", "Author / Year", "Method used", "Result", "Limitation"],
             ["1", f"Yu et al., 2018 {rf('yu18')}", "Survey of edge computing for IoT", "Edge cuts latency and backhaul load", "No priority by event severity"],
             ["2", f"Abbas et al., 2018 {rf('abbas18')}", "Mobile edge computing survey", "Architectures and offloading", "Assumes reliable cellular links"],
             ["3", f"Hassan et al., 2018 {rf('hassan18')}", "Taxonomy of edge paradigms for IoT", "Requirements and open issues", "No evaluation under loss"],
             ["4", f"Pham et al., 2020 {rf('pham20')}", "MEC in 5G and beyond survey", "Resource allocation methods", "5G setting, not marine links"],
             ["5", f"Zhou et al., 2019 {rf('zhou19')}", "Edge intelligence overview", "AI split across device, edge, cloud", "Generic; no disaster case"],
             ["6", f"Esposito et al., 2022 {rf('esposito22')}", "Review of IoT early-warning systems", "Edge/fog layer recommended", "Floods, quakes; not cyclones"],
             ["7", f"Xu et al., 2019 {rf('xu')}", "Review of marine IoT monitoring", "Catalogues ocean sensing systems", "Little on congestion or gaps"],
             ["8", f"Centenaro et al., 2021 {rf('centenaro21')}", "Satellite IoT survey", "LEO links for remote sensors", "Low data rates; no scheduling"],
             ["9", f"Kodheli et al., 2021 {rf('kodheli21')}", "Survey of satellite communications", "Backhaul options and limits", "Not application-aware"],
             ["10", f"Bennis et al., 2018 {rf('bennis18')}", "URLLC: tail latency and risk", "Design for worst case, not average", "Theory; 5G radio focus"],
             ["11", f"Popovski et al., 2018 {rf('popovski18')}", "Building blocks for URLLC", "Reserve resources for urgent data", "Needs 5G infrastructure"],
             ["12", f"Yates et al., 2021 {rf('yates21')}", "Age of information survey", "Freshness metric for status updates", "Not tied to risk level"],
             ["13", f"Fuller et al., 2020 {rf('fuller20')}", "Digital twin review", "Live model mirrored from sensors", "Assumes complete data"],
             ["14", f"Chen et al., 2020 {rf('chenr')}", "Review of ML for cyclone forecasting", "Surveys ML forecast models", "Assumes data already arrived"],
             ["15", f"Chavas & Knaff, 2022 {rf('chavas22')}", "Simple model of storm wind radius", "Realistic wind structure in < 1 s", "Model only, no network"]],
            [0.7, 3.6, 4.1, 4.3, 4.3], "Literature survey (15 articles, 2018–2022)")
    d.p("**Gap:** edge and MEC surveys move computing closer to the data but do not rank traffic by event "
        "severity; URLLC and age-of-information work shows how to protect urgent, fresh data, but on 5G "
        "infrastructure that coastal buoys do not have; and cyclone ML work assumes the data has already arrived. "
        "No work we found ties link priority to the *live* cyclone risk computed at the server, while also repairing "
        "missing readings and showing what was estimated. My part targets exactly this link between risk and the "
        "network.")
    d.p(f"*Foundational methods we also build on (not counted in the 15):* the Holland storm profile {rf('holland')} "
        f"and DiffServ class-based forwarding {rf('diffserv')}.")
    d.h("Proposed Solution Form")
    d.p("**Form: coding and modelling.** We will build the system as software — simulated sensor nodes, an edge "
        "gateway and a central server — plus a network topology in Cisco Packet Tracer. Fabrication or a product "
        "first would be wrong for this problem: we cannot deploy buoys at sea, and the hard part is the *behaviour* "
        "of the network under congestion and loss, which software lets us measure and repeat. Low-cost hardware "
        "nodes can be added later without changing the software design.")
    d.figure(os.path.join(RF, "R1_laksh_proposal.png"), "Proposed block diagram; my parts (server, dashboard, QoS, "
             "network emulation) are highlighted", 15)
    approach(d, "laksh")
    d.h("Initial Technical Feasibility")
    d.table([["Area", "Status"],
             ["Skills I have", "Python, sockets and basic networking, HTML/JavaScript, Git"],
             ["Skills I must learn", "FastAPI web framework, queueing / QoS theory (token bucket), Cisco Packet Tracer "
              "routing (OSPF), writing automated tests with pytest"],
             ["Tools needed / access", "Python 3, FastAPI, uvicorn (free); Cisco Packet Tracer (free with NetAcad "
              "account); own laptop — all available"],
             ["Risks", "No real buoy data (mitigation: physics-based simulation); timing bugs between threads; scope "
              "creep if every feature is attempted before Review 2"]],
            [4.0, 13.0], "Feasibility of my part")
    risks(d, "laksh")
    d.h("Team Role Split and Timeline to Review 2")
    d.table(ROLES["laksh"], [4.2, 4.4, 8.4], "Team role split and interfaces")
    d.p("**My role** is distinct: everything from the moment a packet leaves the gateway — scheduling, the server, "
        "the dashboard — plus the simulation and tests that prove it works.")
    timeline(d, [["1", "25–31 Aug", "Agree the telemetry record format with the team; build the Packet Tracer topology "
                  "(routers, subnets, OSPF)", "Ping from a buoy PC to the prediction server succeeds"],
                 ["2", "1–7 Sep", "Server skeleton: UDP listener, per-node storage, risk score", "Server receives "
                  "packets from the gateway"],
                 ["3", "8–14 Sep", "REST endpoints and first dashboard; end-to-end test with teammates' modules",
                  "Working prototype demonstrated at Review 2"]])
    video(d, VID1, "R1", "laksh")
    rf.write(d)
    finish(d, f"{reg}_LakshAhuja_R1_Report")


# ============================================================================ R1 ANVAY
def r1_anvay():
    name, reg = TEAM[1]
    rf = Refs(["wmo", "chenb", "adt19", "pradhan", "wimmers19", "ruttgers19", "denby", "phisat", "chenran19", "wang20",
               "ray22", "banbury21", "vanhoudt20", "limz", "rudin19", "grinsztajn22", "dvorak", "lstm"])
    d = newdoc(reg, name, "R1", f"{reg}_AnvaySharma_R1")
    cover(d, name, reg, "Review 1 — Problem Identification & Proposal", "24/8/2026",
          "Edge gateway and edge intelligence (classification, satellite image analysis, ML models)",
          "Our project is a cyclone-monitoring network that must work over slow, lossy links. In this report I explain "
          "the problem from the point of view of the network edge: deciding *at the gateway* which data is urgent, "
          "and reducing heavy satellite images to the information that actually matters before they consume the "
          "backbone. I present the evidence, the literature I surveyed, our proposed solution and my plan.")
    d.h("Problem Statement")
    d.p("Edge devices in a cyclone-monitoring network forward everything they receive, in arrival order and at full "
        "size, so a multi-megabyte satellite image or a routine reading can delay the one packet that shows a storm "
        "is intensifying.")
    d.bullets(["**Why it matters:** the earlier a dangerous trend is recognised, the more time there is to warn and "
               "evacuate.",
               "**Who is affected:** fishing communities and coastal residents, and meteorological and disaster "
               "agencies that depend on near-real-time data.",
               "**If unsolved:** a threshold-only system gives **0 s** of warning before a threshold is crossed, and "
               "one raw 2 MB image saturates a 9.6 kbps link for about half an hour."])
    objectives(d, "anvay")
    d.h("Evidence the Problem is Real")
    evidence_table(d, [
        [f"WMO Atlas 1970–2019 {rf('wmo')}", "Storms caused about 577,000 deaths worldwide in 1970–2019 and were the "
         "most common cause of economic damage among weather hazards.", "The cost of recognising danger late is very "
         "high, so even minutes of extra warning matter."],
        [f"Chen et al., 2019 {rf('chenb')}", "The Dvorak method is subjective and gives inconsistent estimates; their "
         "CNN needed 1,097 storms of training data and reached an 8.39 kt error.", "Accurate image analysis exists "
         "but is heavy and central; the edge needs a light version."],
        ["Engineering estimate (our calculation)", "A 4-band 16-bit 512 × 512 frame is 2,097,152 bytes; a record of "
         "about 200 bytes of storm features is roughly 10,000 times smaller.", "Sending features instead of images "
         "is what makes satellite data usable on a slow link."]])
    d.h("Literature Survey")
    d.table([["#", "Author / Year", "Method used", "Result", "Limitation"],
             ["1", f"Olander & Velden, 2019 {rf('adt19')}", "Advanced Dvorak Technique update", "Objective intensity from IR images", "Runs centrally on full images"],
             ["2", f"Pradhan et al., 2018 {rf('pradhan')}", "Deep CNN on IR imagery", "Learned intensity estimation", "Needs GPU and labelled data"],
             ["3", f"Chen et al., 2019 {rf('chenb')}", "CNN on IR + microwave channels", "8.39 kt error on 2017 storms", "Heavy model; central"],
             ["4", f"Wimmers et al., 2019 {rf('wimmers19')}", "Deep learning on passive microwave", "Intensity from microwave images", "Depends on polar passes"],
             ["5", f"Rüttgers et al., 2019 {rf('ruttgers19')}", "GAN on satellite image sequences", "6-h track forecast, ≈96 km error", "Large training set; GPU"],
             ["6", f"Denby & Lucia, 2020 {rf('denby')}", "Orbital edge computing", "Process imagery where captured", "Space segment, not ground"],
             ["7", f"Giuffrida et al., 2022 {rf('phisat')}", "On-board DNN cloud screening", "Discards cloudy frames, saves downlink", "Cloud screening only"],
             ["8", f"Chen & Ran, 2019 {rf('chenran19')}", "Review of deep learning at the edge", "Techniques to fit DL on edge devices", "Mostly video, not sensors"],
             ["9", f"Wang et al., 2020 {rf('wang20')}", "Edge computing + DL survey", "Inference and training at the edge", "No disaster use case"],
             ["10", f"Ray, 2022 {rf('ray22')}", "Review of TinyML", "ML on microcontrollers", "Tools still immature"],
             ["11", f"Banbury et al., 2021 {rf('banbury21')}", "MLPerf Tiny benchmark", "Fair comparison of tiny models", "Benchmark, not application"],
             ["12", f"Van Houdt et al., 2020 {rf('vanhoudt20')}", "Review of the LSTM model", "Formulation, training, uses", "Generic; framework-based"],
             ["13", f"Lim & Zohren, 2021 {rf('limz')}", "Survey of deep time-series forecasting", "Compares RNN, attention, hybrids", "Not edge-constrained"],
             ["14", f"Rudin, 2019 {rf('rudin19')}", "Case for interpretable models", "Simple models for high-stakes use", "Position paper"],
             ["15", f"Grinsztajn et al., 2022 {rf('grinsztajn22')}", "Benchmark: trees vs DL on tables", "Simple models often win on tabular data", "No time-series focus"]],
            [0.7, 3.7, 4.1, 4.3, 4.2], "Literature survey (15 articles, 2018–2022)")
    d.p("**Gap:** image-based cyclone analysis (ADT, CNNs, GANs) runs centrally on full images, and on-board "
        "satellite AI so far only screens out cloudy frames. Edge-AI reviews show how to fit models on small devices "
        "but not for disaster telemetry, and interpretability work argues for simple models where lives are at "
        "stake. Nobody we found extracts storm features at the *ground station* and sends only those, or uses the "
        "*trend* of a sensor's readings at the gateway to raise priority before a threshold is crossed. These two "
        "ideas are my contribution to the project.")
    d.p(f"*Foundational methods we also build on (not counted in the 15):* the Dvorak cloud-pattern technique "
        f"{rf('dvorak')} and the original LSTM {rf('lstm')}.")
    d.h("Proposed Solution Form")
    d.p("**Form: coding and modelling.** The edge gateway and the edge-AI functions are software by nature. We will "
        "first build a rule-based gateway (thresholds on wind and pressure) so the pipeline can be verified, then add "
        "lightweight models that can run on a laptop or a Raspberry Pi. A hardware-first approach was rejected "
        "because the decisions at the edge must be tested on many storm scenarios, which only simulation provides.")
    d.figure(os.path.join(RF, "R1_anvay_proposal.png"), "Proposed block diagram; my parts (gateway classification, edge "
             "image analysis, ML / LSTM) are highlighted", 15)
    approach(d, "anvay")
    d.h("Initial Technical Feasibility")
    d.table([["Area", "Status"],
             ["Skills I have", "Python, NumPy, basic machine learning (regression, classification), threading"],
             ["Skills I must learn", "Image processing on multi-band data, recurrent networks (LSTM) and how to train "
              "them, evaluating models fairly (held-out data, baselines)"],
             ["Tools needed / access", "Python, NumPy, Matplotlib (free); laptop CPU is enough for small models; "
              "real satellite imagery from public portals (MOSDAC) later"],
             ["Risks", "No labelled satellite data (mitigation: synthetic frames with known intensity); ML may raise "
              "false alarms (mitigation: keep the threshold rule as a safety floor); deep-learning frameworks may be "
              "too heavy for edge devices"]],
            [4.0, 13.0], "Feasibility of my part")
    risks(d, "anvay")
    d.h("Team Role Split and Timeline to Review 2")
    d.table(ROLES["anvay"], [4.2, 4.4, 8.4], "Team role split and interfaces")
    d.p("**My role** is the intelligence at the edge: the gateway that classifies and forwards each packet, and the "
        "models that let it recognise danger early and shrink satellite data.")
    timeline(d, [["1", "25–31 Aug", "Define CRITICAL / NORMAL classes and thresholds with the team; design the "
                  "gateway threads (receiver + forwarder)", "Design note and agreed record format"],
                 ["2", "1–7 Sep", "Implement the gateway: UDP receive, threshold classification, priority queue",
                  "Gateway forwards packets in priority order"],
                 ["3", "8–14 Sep", "Alert mode (throttle normal traffic during an alert); integration with sensors and "
                  "server; literature study for the ML classifier", "Gateway shown in the Review 2 demo"]])
    video(d, VID1, "R1", "anvay")
    rf.write(d)
    finish(d, f"{reg}_AnvaySharma_R1_Report")


# ============================================================================ R1 SREEHARI
def r1_sreehari():
    name, reg = TEAM[2]
    rf = Refs(["parri21", "mekki19", "haxhibeqiri18", "jouhari", "xu", "centenaro21", "esposito22", "babiuch19",
               "wimmers19", "grud", "brits", "gain", "csdi21", "saits23", "limz", "gilbert", "elliott"])
    d = newdoc(reg, name, "R1", f"{reg}_Sreehari_R1")
    cover(d, name, reg, "Review 1 — Problem Identification & Proposal", "24/8/2026",
          "Sensing layer (sensor and satellite simulators, hardware nodes) and recovery of lost data",
          "A cyclone-monitoring network is only as good as the data its sensors deliver. In this report I describe "
          "the problem from the sensing side: realistic sensor readings, the lossy links they travel over, and how "
          "lost readings can be recovered. I present the evidence, the 15 articles I studied, the proposed solution "
          "and my plan up to Review 2.")
    d.h("Problem Statement")
    d.p("Ocean buoys and coastal stations lose packets in bursts when storms bring rain fade and interference, so the "
        "monitoring centre receives gaps in the very readings that show a cyclone intensifying.")
    d.bullets(["**Why it matters:** the pressure trend is a key sign of intensification; a gap hides it.",
               "**Who is affected:** forecasters who interpret the data, and coastal communities whose warnings depend "
               "on it.",
               "**If unsolved:** dashboards show missing or stale values during the storm, and models that need "
               "continuous data cannot run. At one reading per second, a 10-minute outage leaves **600 readings** "
               "missing from a single buoy."])
    objectives(d, "sreehari")
    d.h("Evidence the Problem is Real")
    evidence_table(d, [
        [f"Parri et al., 2021 {rf('parri21')}", "A real offshore LoRaWAN link from a buoy to coastal gateways 8.33 km "
         "away was monitored for 70 days, and its signal quality was compared with the weather.", "Marine links work "
         "but their quality changes with conditions, so loss must be expected."],
        [f"Mekki et al., 2019 {rf('mekki19')}", "Low-power wide-area radios trade data rate for range; LoRa runs at "
         "only about 0.3–50 kbps.", "Sensor messages must be small, and lost ones cannot simply be re-sent."],
        ["Engineering estimate (our calculation)", "At 1 reading/s and 10 % loss, about 360 readings per hour are "
         "lost per buoy; in bursts, several consecutive readings vanish together.", "The receiver must recover runs "
         "of missing values, not just single ones."]])
    d.h("Literature Survey")
    d.table([["#", "Author / Year", "Method used", "Result", "Limitation"],
             ["1", f"Parri et al., 2021 {rf('parri21')}", "Offshore LoRaWAN field trial", "8.33 km buoy-to-shore link", "Single site; no data recovery"],
             ["2", f"Mekki et al., 2019 {rf('mekki19')}", "Comparison of LPWAN technologies", "Range vs data-rate trade-offs", "No handling of lost data"],
             ["3", f"Haxhibeqiri et al., 2018 {rf('haxhibeqiri18')}", "LoRaWAN survey", "Capacity and duty-cycle limits", "Not marine-specific"],
             ["4", f"Jouhari et al., 2019 {rf('jouhari')}", "Underwater sensor network survey", "Acoustic, RF and optical links compared", "Underwater focus"],
             ["5", f"Xu et al., 2019 {rf('xu')}", "Review of marine IoT monitoring", "Ocean sensing platforms and links", "Data loss not addressed"],
             ["6", f"Centenaro et al., 2021 {rf('centenaro21')}", "Satellite IoT survey", "Coverage for remote buoys", "Very low throughput"],
             ["7", f"Esposito et al., 2022 {rf('esposito22')}", "IoT early-warning review", "Common sensing architectures", "Assumes data arrives"],
             ["8", f"Babiuch et al., 2019 {rf('babiuch19')}", "ESP32 for measurement and processing", "Low-cost Wi-Fi sensing board", "Lab study, no field test"],
             ["9", f"Wimmers et al., 2019 {rf('wimmers19')}", "Deep learning on microwave imagery", "Shows what satellite channels reveal", "Needs real archives"],
             ["10", f"Che et al., 2018 {rf('grud')}", "GRU-D with missing-value decay", "Better results despite gaps", "Offline clinical data"],
             ["11", f"Cao et al., 2018 {rf('brits')}", "Bidirectional RNN imputation", "Strong gap filling", "Needs whole series"],
             ["12", f"Yoon et al., 2018 {rf('gain')}", "GAN-based imputation (GAIN)", "Imputes without full data", "Hard to train"],
             ["13", f"Tashiro et al., 2021 {rf('csdi21')}", "Diffusion-model imputation (CSDI)", "Probabilistic estimates", "Heavy compute"],
             ["14", f"Du et al., 2023 {rf('saits23')}", "Self-attention imputation (SAITS)", "12–38 % lower error than BRITS", "Offline batches; GPU"],
             ["15", f"Lim & Zohren, 2021 {rf('limz')}", "Deep time-series forecasting survey", "Forecasting model families", "No real-time telemetry"]],
            [0.7, 3.7, 4.1, 4.3, 4.2], "Literature survey (15 articles, 2018–2023)")
    d.p("**Gap:** imputation methods (GRU-D, BRITS, GAIN, CSDI, SAITS) work offline on stored datasets with heavy "
        "frameworks; marine IoT and LPWAN studies describe links but not recovery; and sensor systems are rarely "
        "tested against realistic burst loss with the true values kept for comparison. My part will generate "
        "realistic readings and loss, record the truth so recovery can be measured, recover lost readings online, "
        "and design low-cost nodes that send the same data.")
    d.p(f"*Foundational methods we also build on (not counted in the 15):* the Gilbert–Elliott burst-loss channel "
        f"{rf('gilbert')}, {rf('elliott')}.")
    d.h("Proposed Solution Form")
    d.p("**Form: coding and modelling first, low-cost fabrication later.** Simulated sensor nodes and a simulated "
        "satellite station give us unlimited, repeatable storm scenarios with known ground truth, which is essential "
        "for measuring recovery. Once the software works, ESP32 nodes with a pressure sensor will replace the "
        "simulator using the same message format. A product design was rejected because the scope is a proof of "
        "concept, not a manufactured device.")
    d.figure(os.path.join(RF, "R1_sreehari_proposal.png"), "Proposed block diagram; my parts (sensors, satellite station, "
             "hardware nodes, recovery of lost readings) are highlighted", 15)
    approach(d, "sreehari")
    d.h("Initial Technical Feasibility")
    d.table([["Area", "Status"],
             ["Skills I have", "Python, basic electronics, Arduino programming, statistics"],
             ["Skills I must learn", "Burst-loss channel modelling, time-series reconstruction, ESP32 Wi-Fi/UDP "
              "programming, I²C sensors"],
             ["Tools needed / access", "Python (free); Arduino IDE (free); ESP32 + BMP280 sensor (about ₹500 per node, "
              "college lab may lend); laptop"],
             ["Risks", "No real buoy data (mitigation: physics-inspired simulation); hardware parts delayed "
              "(mitigation: software first); recovery may not beat simple interpolation"]],
            [4.0, 13.0], "Feasibility of my part")
    risks(d, "sreehari")
    d.p("**Initial cost estimate for hardware (R1):** about ₹2,000–2,500 for two nodes including breadboards and "
        "cables; software costs nothing.")
    d.h("Team Role Split and Timeline to Review 2")
    d.table(ROLES["sreehari"], [4.2, 4.4, 8.4], "Team role split and interfaces")
    d.p("**My role** is the beginning of the data path and its repair: what the sensors send, how it gets lost, and "
        "how we recover it.")
    timeline(d, [["1", "25–31 Aug", "Sensor-node simulator: readings, sequence numbers, configurable loss",
                  "Node sends JSON over UDP; LOST lines printed"],
                 ["2", "1–7 Sep", "Cyclone scenario (wind rises, pressure falls) and gap-filling baseline on the server",
                  "Missing sequence numbers are filled and marked"],
                 ["3", "8–14 Sep", "Integration test with gateway and server; hardware parts list", "Prototype shown at "
                  "Review 2; component list ready"]])
    video(d, VID1, "R1", "sreehari")
    rf.write(d)
    finish(d, f"{reg}_Sreehari_R1_Report")


# ============================================================================ R2 shared helpers
R2_RUN = {
    "laksh": ("I re-ran my server, unchanged from repository commit `82bcb8a` (16/9/2026), with three sensor nodes "
              "for 60 seconds to capture dated logs (`docs/reports/evidence/r2_prototype/`). In our original "
              "12-second team test my `/status` endpoint reported 66 packets received, 11 reconstructed and 2 "
              "critical, and `/predict` returned an overall risk of 100 with the alert on."),
    "anvay": ("The gateway evidence below comes from a 60-second re-run of the unmodified Review 2 code (commit "
              "`82bcb8a`) with three nodes; `gateway.log` and `crash_gw.log` are kept in "
              "`docs/reports/evidence/r2_prototype/`. In the team's first 12-second test the server received 66 "
              "packets through my gateway, 2 of them labelled CRITICAL."),
    "sreehari": ("To check my nodes I re-ran the Review 2 prototype (commit `82bcb8a`, no changes) with BUOY_07, "
                 "RADAR_COAST_A and BUOY_12 for 60 seconds; their logs (`buoy_07.log`, `radar.log`, `buoy_12.log`) "
                 "are in `docs/reports/evidence/r2_prototype/`. In the original 12-second team test, the server "
                 "filled 11 readings lost by my two nodes using `reconstruct_gap()`."),
}


# ============================================================================ R2 LAKSH
def r2_laksh():
    name, reg = TEAM[0]
    d = newdoc(reg, name, "R2", f"{reg}_LakshAhuja_R2")
    cover(d, name, reg, "Review 2 — Design, Development & Progress", "14/9/2026",
          "Central server, dashboard, network QoS, cyclone simulation and testing",
          "Since Review 1 I designed and built the central prediction server of our prototype: the UDP listener, "
          "per-node storage, risk scoring, the REST API and a live dashboard, and I worked on the team's Packet "
          "Tracer topology. The prototype runs end to end with my teammates' sensor nodes and gateway. This report "
          "shows the design, the working code, why I chose this design, the updated feasibility, the problems I hit "
          "and how I solved them, and my contribution.")
    d.h("Detailed Design")
    d.p("Input → process → output: **input** is a JSON record forwarded by the gateway over UDP port 9002 "
        "(node, seq, time, wind, temp, pressure, traffic_class); **process** checks the sequence number, fills gaps "
        "using the team's interpolation function, computes a risk score and stores the record; **output** is three "
        "REST endpoints and an HTML dashboard (Figure 2). Figure 1 shows where my modules sit in the whole "
        "prototype.")
    d.figure(os.path.join(RF, "R2_laksh_arch.png"), "Architecture of the R2 prototype; my modules (server, API, "
             "dashboard) are highlighted", 15)
    d.figure(os.path.join(RF, "R2_laksh_server_flow.png"), "Flowchart of my central server (prototype)", 12.5)
    d.table([["Parameter", "Value", "Meaning"],
             ["GATEWAY_TO_SERVER_PORT", "9002 (UDP)", "Where the gateway sends packets"],
             ["HISTORY_LEN", "50", "Readings kept per node (deque)"],
             ["WIND_RISK_THRESHOLD", "60 km/h", "Wind at which the wind part of risk saturates"],
             ["PRESSURE_RISK_THRESHOLD", "990 hPa", "Pressure at which the pressure part saturates"],
             ["Risk formula", "100·(0.6·w + 0.4·p)", "w = min(1, wind/60); p = depression from 1013 towards 990 hPa"],
             ["Alert rule", "max node risk ≥ 60", "Shown in /predict and on the dashboard"],
             ["Dashboard refresh", "2 s polling", "Fetches /predict"]],
            [4.6, 3.6, 8.8], "Labelled parameters of my module")
    d.h("Actual Working Progress since Review 1")
    d.bullets(["**Code committed:** `central_server.py` (189 lines, including the `reconstruct_gap()` function written "
               "by Sreehari), in repository commit `82bcb8a`.",
               "**Running:** server, gateway and sensors run together; endpoints `/predict`, `/status`, "
               "`/telemetry/{node}` and the dashboard work.",
               "**Network:** the team's Packet Tracer topology is complete with OSPF routing; a ping from BUOY-01 to "
               "the prediction server succeeds (Figure 4)."])
    d.p("The heart of the server is short; this is the startup fix and the prediction endpoint:")
    d.code(["@app.on_event(\"startup\")",
            "def start_listener():",
            "    threading.Thread(target=udp_listener, daemon=True).start()",
            "",
            "@app.get(\"/predict\")",
            "def predict():",
            "    with lock:",
            "        latest = {node_id: dq[-1] for node_id, dq in telemetry_store.items() if dq}",
            "    overall = max(rec[\"risk\"] for rec in latest.values())",
            "    return {\"overall_risk\": overall, \"alert\": overall >= 60, \"nodes\": latest}"])
    d.p(R2_RUN["laksh"])
    d.figure(os.path.join(RF, "R2_laksh_status.png"), "My server's /status and /predict during the prototype re-run", 13.5)
    d.figure(os.path.join(AS, "pt_topology.png"), "The team's Packet Tracer topology (joint work); the data-centre "
             "side hosts my prediction and dashboard servers", 13)
    d.figure(os.path.join(AS, "pt_r_core.png"), "Core router configuration (show ip interface brief) linking the WAN "
             "to the data centre", 12)
    d.p("**Completion:** about 40 % of my planned scope. **Done:** server pipeline, risk score, REST API, polling "
        "dashboard, topology. **Remaining:** priority scheduling on a bandwidth-limited link, a learned model for "
        "missing data (with Sreehari and Anvay), real-time updates over WebSocket, a realistic cyclone model, and "
        "automated tests.")
    runs(d, "laksh")
    d.h("Justification of Design Choices")
    d.table([["Choice", "Option", "Cost", "Accuracy / fit", "Availability", "Power", "Ease of use", "Decision"],
             ["Web framework", "Flask", "Free", "Works; background thread needs care", "pip, mature", "Light", "Very easy", "—"],
             ["", "Django", "Free", "Too large for a small API", "pip, mature", "Heavier", "Heavy setup", "—"],
             ["", "**FastAPI**", "Free", "Startup hooks for the UDP thread; auto API docs", "pip, open source", "Light", "Easy", "Chosen"],
             ["Transport", "TCP", "₹0", "Retransmits hide the loss we study; adds delay", "Built into OS", "Extra radio time", "Easy", "—"],
             ["", "MQTT broker", "₹0", "Good later; extra hop", "Mosquitto, free", "Broker always on", "Extra service", "—"],
             ["", "**UDP datagrams**", "₹0", "Loss visible and measurable", "Built into OS", "Least radio time", "Easy", "Chosen"],
             ["Dashboard", "**Polling 2 s**", "₹0", "Up to 2 s stale", "Any browser", "Small repeated requests", "Simplest", "Chosen now"],
             ["", "WebSocket push", "₹0", "Instant updates", "Needs extra package", "Fewer requests", "Moderate", "Next phase"],
             ["Hosting", "**Own laptop**", "₹0", "Enough for demos", "Available now", "Laptop only", "Easy", "Chosen"],
             ["", "Cloud VM", "≈US$5–10 / month", "Public URL", "Needs payment card", "Data centre", "Moderate", "Later"]],
            [1.9, 2.7, 1.5, 3.1, 2.4, 2.0, 1.8, 1.6], "Comparison of alternatives for my module (cost, accuracy, availability, power, ease of use)")
    d.h("Updated Feasibility")
    d.table([["Aspect", "Review 1 estimate", "Now (Review 2)", "Reason for change"],
             ["Software cost", "₹0", "₹0", "All tools open source"],
             ["Server hosting", "Own laptop", "Own laptop; a small cloud VM later ≈ US$5–10 / month", "Needed only for a "
              "public demo"],
             ["Effort", "3 weeks for prototype", "On schedule", "Startup race fixed in one day"]],
            [3.2, 3.8, 5.0, 5.0], "Economic picture for my part")
    d.p("**Social:** coastal and island communities often have the worst connectivity, so a server that keeps a "
        "usable picture despite missing data supports fairer disaster response. **Environmental:** no new hardware "
        "is needed for the server tier, and avoiding retransmissions saves energy at the remote end.")
    d.h("Problems Encountered and How I Adapted")
    d.table([["Problem", "How I diagnosed it", "What I changed", "Result"],
             ["`/predict` returned empty data at first", "Server log showed the listener starting after sensors had "
              "begun sending; the thread was started at import time", "Start the UDP listener in FastAPI's startup "
              "event", "Data appears immediately; fixed"],
             ["Processes started from separate shells failed silently", "Background processes lost their working "
              "directory, so imports failed", "Launch the server, gateway and sensors from one script", "All "
              "components start reliably; fixed"],
             ["One malformed packet stopped the server receiving", "Sent a non-JSON datagram during testing: the "
              "listener thread raised an exception and died; `/status` then showed 0 packets received",
              "Input validation and exception handling planned for the next phase", "Workaround: restart; fix "
              "scheduled"],
             ["Gaps can only be repaired after the next packet", "Found while reviewing the logs: a gap is known only "
              "when a later sequence number arrives", "Plan real-time estimates for overdue packets", "Design "
              "limitation recorded"]],
            [3.6, 5.0, 4.4, 4.0], "Problems in my module")
    plan3(d, "laksh")
    d.h("Individual Contribution Evidence")
    d.table([["Tasks I did", "Tasks done by teammates"],
             ["Central server: UDP listener, storage, risk score, alert rule", "Anvay: edge gateway (classification, "
              "priority queue, alert throttling)"],
             ["REST API (/predict, /status, /telemetry) and HTML dashboard", "Sreehari: sensor-node simulator and the "
              "reconstruct_gap() interpolation used by my server"],
             ["Startup race fix; single-script launch; end-to-end test runs", "Team: shared record format (common.py), "
              "Packet Tracer topology"]], [8.5, 8.5], "Division of work")
    d.bullets(["Code: `central_server.py` at commit `82bcb8a` (" + REPO_URL + ").",
               "Logs: `server.log`, `api.log` and `crash_srv.log` in `docs/reports/evidence/r2_prototype/`."])
    contrib_placeholder(d, "laksh")
    video(d, VID2, "R2", "laksh")
    finish(d, f"{reg}_LakshAhuja_R2_Report")


# ============================================================================ R2 ANVAY
def r2_anvay():
    name, reg = TEAM[1]
    d = newdoc(reg, name, "R2", f"{reg}_AnvaySharma_R2")
    cover(d, name, reg, "Review 2 — Design, Development & Progress", "14/9/2026",
          "Edge gateway and edge intelligence",
          "Since Review 1 I built the edge gateway of our prototype: it receives every sensor packet, classifies it as "
          "CRITICAL or NORMAL against cyclone thresholds, forwards critical packets first through a priority queue, "
          "and throttles normal traffic while a cyclone alert is active. This report covers the gateway's design, "
          "the working code, my design choices, feasibility, the problems I found by testing it, and my contribution.")
    d.h("Detailed Design")
    d.figure(os.path.join(RF, "R2_anvay_arch.png"), "Architecture of the R2 prototype; my modules (gateway and "
             "classification rule) are highlighted", 15)
    d.p("Figure 1 shows where the gateway sits between the sensors and the server. It has two threads (Figure 2). The **receiver** reads UDP port 9001, decodes the record, classifies "
        "it and pushes (priority, order, record) into a priority queue. The **forwarder** takes the highest-priority "
        "record and sends it to the server on port 9002; while an alert is active, each NORMAL packet waits 0.5 s "
        "first. The alert switches on with any CRITICAL packet and clears after 10 s without one.")
    d.figure(os.path.join(RF, "R2_anvay_gateway_flow.png"), "Flowchart of my edge gateway (prototype)", 12.5)
    d.table([["Parameter", "Value", "Meaning"],
             ["SENSOR_TO_GATEWAY_PORT", "9001 (UDP)", "Input from sensor nodes"],
             ["GATEWAY_TO_SERVER_PORT", "9002 (UDP)", "Output to the central server"],
             ["WIND_CRITICAL_THRESHOLD", "60 km/h", "CRITICAL if wind ≥ this"],
             ["PRESSURE_CRITICAL_THRESHOLD", "990 hPa", "CRITICAL if pressure ≤ this"],
             ["Priority", "0 = CRITICAL, 1 = NORMAL", "Lower value served first; insertion order breaks ties"],
             ["ALERT_HOLD_SECONDS", "10 s", "Alert stays on this long after the last CRITICAL packet"],
             ["Throttle", "0.5 s per NORMAL packet", "Applied only while the alert is active"]],
            [4.8, 4.2, 8.0], "Labelled parameters of my module")
    d.h("Actual Working Progress since Review 1")
    d.bullets(["**Code committed:** `edge_gateway.py` (101 lines) and the `classify_traffic()` rule in `common.py`, "
               "commit `82bcb8a`.",
               "**Running:** the gateway receives from three nodes and forwards in priority order; the log shows the "
               "alert switching on and NORMAL packets being throttled.",
               "**Studied for the next phase:** trend-based ML classification and satellite feature extraction "
               "(literature from Review 1)."])
    d.code(["def classify_traffic(record):",
            "    if record[\"wind\"] >= WIND_CRITICAL_THRESHOLD or record[\"pressure\"] <= PRESSURE_CRITICAL_THRESHOLD:",
            "        return TRAFFIC_CRITICAL",
            "    return TRAFFIC_NORMAL",
            "",
            "# forwarder thread",
            "_priority, _order, record = pq.get()",
            "if record[\"traffic_class\"] != TRAFFIC_CRITICAL and cyclone_alert.is_set():",
            "    time.sleep(0.5)            # reserve bandwidth for critical traffic",
            "sock.sendto(encode(record), (HOST, GATEWAY_TO_SERVER_PORT))"])
    d.p(R2_RUN["anvay"])
    d.figure(os.path.join(RF, "R2_anvay_gateway.png"), "Classification over time in the re-run (from my gateway's log)", 13.5)
    d.p("In the re-run the gateway forwarded 160 packets: 42 CRITICAL packets were sent immediately, and 28 NORMAL "
        "packets were throttled during the alert.")
    d.figure(os.path.join(AS, "pt_r_ocean.png"), "Ocean-side router of the team's Packet Tracer topology (joint work); "
             "this is the edge of the network where my gateway sits", 12)
    d.p("**Completion:** about 40 % of my planned scope. **Done:** gateway pipeline, threshold classification, priority "
        "forwarding, alert mode. **Remaining:** input validation, an ML early-warning classifier, satellite image "
        "feature extraction, an LSTM for missing data, and a proper evaluation.")
    runs(d, "anvay")
    d.h("Justification of Design Choices")
    d.table([["Choice", "Option", "Cost", "Accuracy / fit", "Availability", "Power", "Ease of use", "Decision"],
             ["Classifier", "**Threshold rule**", "₹0", "Exact on breaches; no early warning", "Ready in common.py", "Negligible", "Very easy", "Chosen now"],
             ["", "Logistic regression on trends", "₹0", "Can warn before a breach", "NumPy (free)", "Very low", "Easy", "Next phase"],
             ["", "Deep network", "GPU or paid cloud", "Possibly best", "Needs labelled data we lack", "High", "Hard", "Rejected"],
             ["Forwarding", "FIFO queue", "₹0", "Critical waits behind others", "Standard library", "Low", "Easiest", "Rejected"],
             ["", "Fixed cap per class", "₹0", "Wastes capacity when idle", "Standard library", "Low", "Easy", "Rejected"],
             ["", "**Priority queue**", "₹0", "Critical first; adapts instantly", "queue.PriorityQueue", "Low", "Easy", "Chosen"],
             ["Edge device", "**Laptop**", "Owned", "Fast enough (< 1 % CPU)", "Available now", "≈30–60 W", "Easy", "Chosen"],
             ["", "Raspberry Pi 4", "≈₹5,000", "Fast enough", "College lab", "≈3–6 W", "Moderate", "Optional"]],
            [1.9, 2.7, 1.5, 3.1, 2.4, 2.0, 1.8, 1.6], "Comparison of alternatives for my module (cost, accuracy, availability, power, ease of use)")
    d.h("Updated Feasibility")
    d.table([["Aspect", "Review 1 estimate", "Now (Review 2)", "Reason"],
             ["Software cost", "₹0", "₹0", "Python standard library only"],
             ["Edge hardware", "Laptop or Raspberry Pi", "Laptop; Pi optional (lab)", "Gateway uses < 1 % CPU"],
             ["ML compute", "Possibly GPU", "CPU only", "Lightweight models chosen to fit the edge"]],
            [3.2, 3.8, 5.0, 5.0], "Economic picture for my part")
    d.p("**Social:** earlier recognition of danger directly benefits people who must evacuate. **Environmental:** "
        "choosing small CPU models instead of GPU training keeps energy use low, and prioritising data avoids wasteful "
        "retransmissions on remote links.")
    d.h("Problems Encountered and How I Adapted")
    d.table([["Problem", "How I diagnosed it", "What I changed", "Result"],
             ["A malformed packet stopped the gateway", "Sent a non-JSON datagram while testing: the receiver thread "
              "raised an exception in decode() and died; later valid packets were ignored", "Added a validation step "
              "to the design (check fields and ranges, count and drop bad packets)", "To be implemented next; logged as "
              "the top fix"],
             ["NORMAL packets delayed even on an idle link", "Log showed 28 NORMAL packets each waiting 0.5 s during "
              "the alert although the queue was empty; a fixed sleep ignores real link capacity", "Plan a "
              "capacity-based scheduler (token bucket) instead of a fixed sleep", "Behaviour understood; redesign "
              "scheduled"],
             ["Alert state can be stale", "Code review: the alert is cleared only before the forwarder blocks on the "
              "queue, so a NORMAL packet arriving after a long silence is still throttled", "Re-check the alert after "
              "every dequeue in the redesign", "Identified before it affected a demo"]],
            [3.6, 5.0, 4.4, 4.0], "Problems in my module")
    plan3(d, "anvay")
    d.h("Individual Contribution Evidence")
    d.table([["Tasks I did", "Tasks done by teammates"],
             ["Edge gateway: receiver and forwarder threads, priority queue", "Laksh: central server, REST API, "
              "dashboard, startup fix"],
             ["CRITICAL / NORMAL rule (classify_traffic) and alert mode", "Sreehari: sensor-node simulator and gap "
              "interpolation"],
             ["Robustness testing of the gateway (malformed input, throttling)", "Team: shared record format, Packet "
              "Tracer topology"]], [8.5, 8.5], "Division of work")
    d.bullets(["Code: `edge_gateway.py` and `classify_traffic()` in `common.py`, commit `82bcb8a` (" + REPO_URL + ").",
               "Logs: `gateway.log` and `crash_gw.log` in `docs/reports/evidence/r2_prototype/`."])
    contrib_placeholder(d, "anvay")
    video(d, VID2, "R2", "anvay")
    finish(d, f"{reg}_AnvaySharma_R2_Report")


# ============================================================================ R2 SREEHARI
def r2_sreehari():
    name, reg = TEAM[2]
    d = newdoc(reg, name, "R2", f"{reg}_Sreehari_R2")
    cover(d, name, reg, "Review 2 — Design, Development & Progress", "14/9/2026",
          "Sensing layer, hardware and recovery of lost data",
          "Since Review 1 I built the sensor-node simulator of our prototype and the function that fills gaps left by "
          "lost packets, and I prepared the hardware parts list. The sensor nodes generate a cyclone scenario, drop "
          "packets to emulate a lossy marine link, and the server repairs the missing sequence numbers. This report "
          "covers the design, the working code, my choices, updated costs, the problems I found and my contribution.")
    d.h("Detailed Design")
    d.p("**Sensor node:** every second the node increments its sequence number, updates wind, temperature and "
        "pressure (a small random walk in calm weather; after `--cyclone-after` seconds wind rises and pressure "
        "falls), builds a compact JSON record and, unless the loss draw says the packet is lost, sends it to the "
        "gateway. **Gap filling:** when the server sees a jump in sequence numbers, my `reconstruct_gap()` linearly "
        "interpolates each variable between the readings before and after the gap and marks the result as "
        "reconstructed (Figure 2). Figure 1 places my modules in the whole prototype.")
    d.figure(os.path.join(RF, "R2_sreehari_arch.png"), "Architecture of the R2 prototype; my modules (sensor nodes, "
             "gap filling, planned ESP32 node) are highlighted", 15)
    d.figure(os.path.join(RF, "R2_sreehari_sensor_flow.png"), "Flowchart of my sensor node and gap filling (prototype)", 12.5)
    d.table([["Parameter", "Value", "Meaning"],
             ["--interval", "1 s", "Time between readings"],
             ["--loss", "0.08 default (0.10–0.15 in tests)", "Probability that a packet is dropped"],
             ["--cyclone-after", "20 s default", "When the storm starts in the scenario"],
             ["Calm walk", "wind ±1, pressure ±0.5, temp ±0.2 per step", "Natural variation"],
             ["Cyclone ramp", "wind +0.5…3 (max 120), pressure −0.2…1.5 (min 930)", "Approaching storm"],
             ["Interpolation", "x_k = x_prev + (k/gap)·(x_curr − x_prev)", "Estimate for missing reading k"]],
            [3.4, 6.4, 7.2], "Labelled parameters of my module")
    d.h("Actual Working Progress since Review 1")
    d.bullets(["**Code committed:** `sensor_node.py` (68 lines) and `reconstruct_gap()` in `central_server.py`, commit "
               "`82bcb8a`.",
               "**Running:** three simulated nodes (BUOY_07, RADAR_COAST_A, BUOY_12) with different loss rates and "
               "cyclone start times feed the gateway; the server marks filled readings as reconstructed.",
               "**Hardware:** parts list prepared (ESP32 + BMP280 per node); purchase planned after the software "
               "interface is fixed. The circuit is designed (Figure 3) so that the node sends exactly the same "
               "JSON as the simulator."])
    d.figure(os.path.join(RF, "R2_sreehari_circuit.png"), "Circuit diagram of the planned ESP32 buoy node "
             "(BMP280 on I²C, potentiometer as wind input, buzzer and LED for local alert)", 15)
    d.code(["if random.random() < loss_rate:",
            "    print(f\"[{node_id}] seq={seq:05d} LOST (simulated link loss)\")",
            "else:",
            "    sock.sendto(encode(record), (HOST, SENSOR_TO_GATEWAY_PORT))",
            "",
            "def reconstruct_gap(node_id, prev_record, curr_record):",
            "    gap = curr_record[\"seq\"] - prev_record[\"seq\"]",
            "    for i in range(1, gap):",
            "        frac = i / gap      # linear interpolation for each variable"])
    d.p(R2_RUN["sreehari"])
    d.figure(os.path.join(RF, "R2_sreehari_sensor.png"), "Output of my sensor node in the re-run; red lines mark lost packets", 13.5)
    d.p("In the re-run my three nodes lost 22 packets in total; the server filled them using my function (22 "
        "reconstructed in `/status` at 60 s).")
    d.figure(os.path.join(AS, "pt_buoy1_ip.png"), "BUOY-1 end device in the team's Packet Tracer topology (joint work); "
             "it represents my sensor nodes in the routed network", 13)
    d.p("**Completion:** about 40 % of my planned scope. **Done:** sensor simulator, cyclone scenario, loss emulation, "
        "interpolation baseline, parts list. **Remaining:** realistic storm physics and bursty loss, ground-truth "
        "logging, a learned reconstruction model, a satellite-station simulator, and the ESP32 nodes.")
    runs(d, "sreehari")
    d.h("Justification of Design Choices")
    d.table([["Choice", "Option", "Cost", "Accuracy / fit", "Availability", "Power", "Ease of use", "Decision"],
             ["Data source", "**Simulated nodes**", "₹0", "Controllable; true values known", "Instant", "None", "Easiest", "Chosen now"],
             ["", "Recorded buoy archives", "₹0", "Real, but loss not controllable", "Public portals (registration)", "None", "Needs cleaning", "Later"],
             ["", "ESP32 hardware nodes", "≈₹800 / node", "Real sensors, real Wi-Fi loss", "Local shops / online", "≈0.5 W sending; deep sleep", "Build effort", "Next phase"],
             ["Gap filling", "Hold last value", "₹0", "Poor when values change fast", "Trivial", "Negligible", "Trivial", "Rejected"],
             ["", "**Linear interpolation**", "₹0", "Good baseline; needs next reading", "Own code", "Negligible", "Easy", "Chosen now"],
             ["", "LSTM / GRU-D", "₹0", "Can learn storm dynamics", "Own NumPy code", "Training on laptop CPU", "Needs training", "Next phase"],
             ["Micro-controller", "Arduino Uno + ESP8266", "≈₹700", "Works", "Common", "Two boards", "Extra wiring", "Rejected"],
             ["", "**ESP32**", "≈₹400", "Wi-Fi built in", "Very common", "Deep sleep available", "Arduino IDE", "Planned"],
             ["Pressure sensor", "**BMP280**", "≈₹120", "±1 hPa absolute", "Very common", "Very low", "I²C, 4 wires", "Planned"],
             ["", "BME280", "≈₹350", "Adds humidity", "Common", "Very low", "I²C, 4 wires", "Rejected (cost)"]],
            [1.9, 2.7, 1.5, 3.1, 2.4, 2.0, 1.8, 1.6], "Comparison of alternatives for my module (cost, accuracy, availability, power, ease of use)")
    d.h("Updated Feasibility")
    d.table([["Aspect", "Review 1 estimate", "Now (Review 2)", "Reason for change"],
             ["Two hardware nodes", "₹2,000–2,500", "₹1,600–2,200", "BMP280 (≈₹120) chosen instead of BME280; a "
              "potentiometer replaces a commercial anemometer for demos"],
             ["Software", "₹0", "₹0", "Python and Arduino IDE are free"],
             ["Purchase status", "—", "Not yet bought", "Waiting until the message format is final"]],
            [3.2, 3.6, 3.4, 6.8], "Economic picture for my part")
    d.p("**Social:** low-cost nodes would let local bodies and colleges densify coastal monitoring. "
        "**Environmental:** ESP32 boards are reusable and can sleep between readings; small packets mean less radio "
        "energy.")
    d.h("Problems Encountered and How I Adapted")
    d.table([["Problem", "How I diagnosed it", "What I changed", "Result"],
             ["Simulated losses are unrealistically scattered", "Counted runs of LOST lines in the re-run logs: 22 "
              "losses, the longest run only 2 packets; real storm links lose packets in bursts", "Plan a two-state "
              "burst-loss (Gilbert–Elliott) model", "Problem quantified; model chosen"],
             ["The simulated cyclone never passes", "Simulated 300 steps of my node's logic: wind stays at 120 km/h and "
              "pressure at 930 hPa after about 100 s, so the alert can never clear", "Plan a storm that approaches, "
              "passes and recedes (physical wind/pressure profile)", "Needed to test alert clearing"],
             ["Reconstructed readings had the wrong time", "Unit check of reconstruct_gap(): readings 11 and 12 both "
              "got 12:00:03, the time of packet 13", "Mark them as estimates of their own sequence slot; correct time "
              "stamping planned", "Bug found before it affected results"],
             ["Cannot measure how good the gap filling is", "Lost readings are never recorded anywhere, so there is "
              "no truth to compare with", "Plan a ground-truth log written by each node, including lost readings",
              "Enables error measurement next phase"]],
            [3.6, 5.0, 4.4, 4.0], "Problems in my module")
    plan3(d, "sreehari")
    d.h("Individual Contribution Evidence")
    d.table([["Tasks I did", "Tasks done by teammates"],
             ["Sensor-node simulator: readings, sequence numbers, cyclone ramp, loss emulation", "Laksh: central "
              "server, REST API, dashboard"],
             ["reconstruct_gap() interpolation used by the server", "Anvay: edge gateway classification and priority "
              "forwarding"],
             ["Hardware parts list and cost estimate; loss and gap analysis of the logs", "Team: shared record format, "
              "Packet Tracer topology"]], [8.5, 8.5], "Division of work")
    d.bullets(["Code: `sensor_node.py` and `reconstruct_gap()` in `central_server.py`, commit `82bcb8a` (" + REPO_URL + ").",
               "Logs: `buoy_07.log`, `buoy_12.log`, `radar.log` and `server.log` in `docs/reports/evidence/r2_prototype/`."])
    contrib_placeholder(d, "sreehari")
    video(d, VID2, "R2", "sreehari")
    finish(d, f"{reg}_Sreehari_R2_Report")


if __name__ == "__main__":
    for fn in (r1_laksh, r1_anvay, r1_sreehari, r2_laksh, r2_anvay, r2_sreehari):
        fn()
