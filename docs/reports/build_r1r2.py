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
})

ROLES = [["Member", "Role", "Specific tasks (R1 → R3)"],
         ["Laksh Ahuja (24BDS0212)", "Central server, dashboard & network QoS",
          "Prediction server and REST API, live dashboard, priority scheduling on the slow link, cyclone simulation "
          "model, demo launcher, automated testing"],
         ["Anvay Sharma (24BCE0824)", "Edge gateway & edge intelligence",
          "Gateway classification and forwarding, satellite image analysis at the edge, ML early-warning classifier, "
          "LSTM implementation, evaluation and logs"],
         ["Sreehari (24BDS0417)", "Sensing layer, hardware & data recovery",
          "Sensor-node and satellite-station simulators, packet-loss model, reconstruction of lost readings, model "
          "training data, ESP32 hardware nodes"]]


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


def evidence_table(d, rf, angle):
    rows = [["Source", "Published fact", "Why it matters for my part"],
            [f"India Meteorological Department {rf('imd')}", "India has a coastline of about 7,500 km; the 1999 Odisha "
             "super cyclone caused about 10,000 deaths.", angle[0]],
            [f"WMO Atlas 1970–2019 {rf('wmo')}", "Tropical cyclones are among the leading causes of human and economic "
             "losses from weather, climate and water extremes.", angle[1]],
            ["Engineering estimate (our calculation)", angle[2][0], angle[2][1]]]
    d.table(rows, [4.0, 6.5, 6.5], "Evidence that the problem is real")


def timeline(d, weeks):
    d.table([["Week", "Dates", "My milestone", "Deliverable / check"]] + weeks, [1.6, 2.8, 7.2, 5.4],
            "My weekly plan from Review 1 to Review 2")


def contrib_placeholder(d):
    d.note("[Insert here: screenshot of my own commits / work log and a photo or screen recording of me testing. "
           "Note: the team's early commits were pushed from one shared GitHub account, so the file-level split "
           "above is the record of who wrote what.]")


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


def video(d, items, review):
    d.h(f"{review} Video Plan", 2, numbered=False)
    d.table([["Segment", "What I show"]] + [[a, "Face + screen; " + b] for a, b in zip(items, VIDEO_SHOW[review])],
            [6.0, 11.0])


def runs(d, who):
    d.table([["Test run", "Setup", "Observation"]] + RUNS[who], [4.0, 5.4, 7.6], "Test runs performed on my module")


def plan3(d, who):
    d.h("Plan from Review 2 to Review 3", 2, numbered=False)
    d.table([["Week", "Planned work"]] + PLAN3[who], [3.0, 14.0])


VIDEO_SHOW = {
    "R1": ["IMD / WMO evidence and the problem statement", "literature table and the gap", "block diagram and feasibility table",
           "role table and weekly plan"],
    "R2": ["flowchart and parameter table", "code running and the logs", "the problem table and the evidence log",
           "cost table and the division-of-work table"],
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
    rf = Refs(["imd", "wmo", "shi", "satya", "mao", "bonomi", "alfuqaha", "xu", "diffserv", "red", "drr", "mininet",
               "mqtt", "holland", "pradhan", "grud", "chenr"])
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
               "equally; under congestion, critical readings queue behind unimportant data, and gaps from packet "
               "loss leave the dashboard blank or wrong during the critical hours."])
    objectives(d, "laksh")
    d.h("Evidence the Problem is Real")
    evidence_table(d, rf, ["A large exposed population depends on timely data from coastal sensors.",
                           "The cost of a late warning is measured in lives and livelihoods.",
                           ("One 4-band, 16-bit satellite frame of 512 × 512 pixels is about 2.1 MB; on a 9.6 kbps "
                            "satellite backhaul that alone would take roughly half an hour to send.",
                            "Shows why the network must decide what to send first — the core of my QoS work.")])
    d.h("Literature Survey")
    d.table([["#", "Author / Year", "Method used", "Result", "Limitation"],
             ["1", f"Shi et al., 2016 {rf('shi')}", "Edge computing vision paper", "Defines edge tier, motivates local processing", "No concrete scheduling policy"],
             ["2", f"Satyanarayanan, 2017 {rf('satya')}", "Cloudlet / edge architecture", "Lower latency and backhaul load", "General purpose; no disaster focus"],
             ["3", f"Mao et al., 2017 {rf('mao')}", "Survey of mobile edge computing", "Taxonomy of offloading and resource allocation", "Cellular setting; not lossy marine links"],
             ["4", f"Bonomi et al., 2012 {rf('bonomi')}", "Fog computing for IoT", "Argues for a layer between devices and cloud", "Position paper; no evaluation"],
             ["5", f"Al-Fuqaha et al., 2015 {rf('alfuqaha')}", "IoT protocol survey", "Compares MQTT, CoAP and others", "No prioritisation by event severity"],
             ["6", f"Xu et al., 2019 {rf('xu')}", "Review of marine IoT monitoring", "Catalogues ocean sensing systems", "Little on congestion or data gaps"],
             ["7", f"Blake et al., 1998 {rf('diffserv')}", "DiffServ class-based QoS", "Scalable per-hop priority", "Classes fixed in advance"],
             ["8", f"Floyd & Jacobson, 1993 {rf('red')}", "Random early detection", "Keeps queues short", "Drops are blind to importance"],
             ["9", f"Shreedhar & Varghese, 1996 {rf('drr')}", "Deficit round-robin", "Fair sharing in O(1)", "Fairness, not urgency"],
             ["10", f"Lantz et al., 2010 {rf('mininet')}", "Mininet emulation", "Realistic networks on one laptop", "Tool only"],
             ["11", f"Banks & Gupta, 2014 {rf('mqtt')}", "MQTT 3.1.1 standard", "Lightweight publish/subscribe", "QoS levels about delivery, not urgency"],
             ["12", f"Holland, 1980 {rf('holland')}", "Analytic hurricane wind/pressure profile", "Standard parametric storm model", "Not a monitoring system"],
             ["13", f"Pradhan et al., 2018 {rf('pradhan')}", "CNN on satellite images", "Automatic intensity estimation", "Central, compute-heavy"],
             ["14", f"Che et al., 2018 {rf('grud')}", "RNN for series with missing values", "Better predictions despite gaps", "Offline; not a live server"],
             ["15", f"Chen et al., 2020 {rf('chenr')}", "Review of ML for cyclone forecasting", "Surveys ML forecast models", "Focus on models, not data delivery"]],
            [0.7, 3.4, 4.2, 4.4, 4.3], "Literature survey (15 articles)")
    d.p("**Gap:** networking work (DiffServ, RED, DRR) prioritises traffic by fixed rules, edge papers stay at the "
        "level of vision, and cyclone ML work assumes the data has already arrived. No work we found ties network "
        "priority to the *live* cyclone risk computed at the server, while also repairing missing readings and "
        "showing what was estimated. My part of the project targets exactly this link between risk and the network.")
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
    d.table(ROLES, [4.2, 4.4, 8.4], "Team role split")
    d.p("**My role** is distinct: everything from the moment a packet leaves the gateway — scheduling, the server, "
        "the dashboard — plus the simulation and tests that prove it works.")
    timeline(d, [["1", "25–31 Aug", "Agree the telemetry record format with the team; build the Packet Tracer topology "
                  "(routers, subnets, OSPF)", "Ping from a buoy PC to the prediction server succeeds"],
                 ["2", "1–7 Sep", "Server skeleton: UDP listener, per-node storage, risk score", "Server receives "
                  "packets from the gateway"],
                 ["3", "8–14 Sep", "REST endpoints and first dashboard; end-to-end test with teammates' modules",
                  "Working prototype demonstrated at Review 2"]])
    video(d, VID1, "R1")
    rf.write(d)
    finish(d, f"{reg}_LakshAhuja_R1_Report")


# ============================================================================ R1 ANVAY
def r1_anvay():
    name, reg = TEAM[1]
    rf = Refs(["imd", "wmo", "dvorak", "velden", "adt", "pradhan", "chenb", "chenr", "denby", "phisat", "lstm",
               "limz", "xgb", "shi", "mao", "coap", "diffserv"])
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
               "**If unsolved:** a threshold-only system gives zero warning before a threshold is crossed, and raw "
               "images can saturate the link for many minutes."])
    objectives(d, "anvay")
    d.h("Evidence the Problem is Real")
    evidence_table(d, rf, ["The scale of exposure makes early warning valuable.",
                           "Losses justify investing in faster, smarter edge decisions.",
                           ("A 4-band 16-bit frame at 512 × 512 pixels is 2,097,152 bytes; lossless compression "
                            "typically removes only a fraction of that for noisy imagery.",
                            "Sending images unprocessed is not viable; edge analysis must cut data volume by orders "
                            "of magnitude.")])
    d.h("Literature Survey")
    d.table([["#", "Author / Year", "Method used", "Result", "Limitation"],
             ["1", f"Dvorak, 1975 {rf('dvorak')}", "Analyst reads cloud patterns in satellite images", "Global operational standard", "Subjective; needs experts"],
             ["2", f"Velden et al., 2006 {rf('velden')}", "30-year review of the Dvorak technique", "Documents accuracy and pitfalls", "No automation for edge devices"],
             ["3", f"Olander & Velden, 2007 {rf('adt')}", "Advanced Dvorak Technique (objective, IR)", "Automated intensity estimates", "Runs centrally on full images"],
             ["4", f"Pradhan et al., 2018 {rf('pradhan')}", "Deep CNN on IR imagery", "Learned intensity estimation", "Needs GPU and large labelled data"],
             ["5", f"Chen et al., 2019 {rf('chenb')}", "CNN using multi-channel satellite data", "Improved intensity estimates", "Heavy model; central processing"],
             ["6", f"Chen et al., 2020 {rf('chenr')}", "Review of ML in cyclone forecasting", "Maps ML methods to forecast tasks", "No network or edge aspect"],
             ["7", f"Denby & Lucia, 2020 {rf('denby')}", "Orbital edge computing on nanosatellites", "Process imagery where it is captured", "Space segment, not ground stations"],
             ["8", f"Giuffrida et al., 2022 {rf('phisat')}", "On-board DNN filters cloudy images (Φ-Sat-1)", "Saves downlink by discarding useless data", "Cloud screening only, not storm features"],
             ["9", f"Hochreiter & Schmidhuber, 1997 {rf('lstm')}", "LSTM recurrent network", "Learns long time dependencies", "Generic; needs a framework"],
             ["10", f"Lim & Zohren, 2021 {rf('limz')}", "Survey of deep time-series forecasting", "Compares RNN, attention, hybrids", "Not edge-constrained"],
             ["11", f"Chen & Guestrin, 2016 {rf('xgb')}", "Gradient-boosted trees (XGBoost)", "Strong tabular classifier", "Less transparent than linear models"],
             ["12", f"Shi et al., 2016 {rf('shi')}", "Edge computing vision", "Motivates edge analytics", "No algorithms"],
             ["13", f"Mao et al., 2017 {rf('mao')}", "Mobile edge computing survey", "Offloading decisions at the edge", "Cellular focus"],
             ["14", f"Shelby et al., 2014 {rf('coap')}", "CoAP protocol", "Compact messages for constrained devices", "No content-aware priority"],
             ["15", f"Blake et al., 1998 {rf('diffserv')}", "DiffServ traffic classes", "Class-based forwarding", "Static classification"]],
            [0.7, 3.4, 4.2, 4.4, 4.3], "Literature survey (15 articles)")
    d.p("**Gap:** image-based cyclone analysis (Dvorak, ADT, CNNs) runs centrally on full images, and on-board "
        "satellite AI so far only screens out cloudy frames. Network classification uses fixed rules on current "
        "values. Nobody we found extracts storm features at the *ground station* and sends only those, or uses the "
        "*trend* of a sensor's readings at the gateway to raise priority before a threshold is crossed. These two "
        "ideas are my contribution to the project.")
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
    d.table(ROLES, [4.2, 4.4, 8.4], "Team role split")
    d.p("**My role** is the intelligence at the edge: the gateway that classifies and forwards each packet, and the "
        "models that let it recognise danger early and shrink satellite data.")
    timeline(d, [["1", "25–31 Aug", "Define CRITICAL / NORMAL classes and thresholds with the team; design the "
                  "gateway threads (receiver + forwarder)", "Design note and agreed record format"],
                 ["2", "1–7 Sep", "Implement the gateway: UDP receive, threshold classification, priority queue",
                  "Gateway forwards packets in priority order"],
                 ["3", "8–14 Sep", "Alert mode (throttle normal traffic during an alert); integration with sensors and "
                  "server; literature study for the ML classifier", "Gateway shown in the Review 2 demo"]])
    video(d, VID1, "R1")
    rf.write(d)
    finish(d, f"{reg}_AnvaySharma_R1_Report")


# ============================================================================ R1 SREEHARI
def r1_sreehari():
    name, reg = TEAM[2]
    rf = Refs(["imd", "wmo", "alfuqaha", "xu", "raza", "lora", "jouhari", "gilbert", "elliott", "grud", "brits",
               "gain", "limz", "holland", "chenb", "denby", "coap"])
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
               "continuous data cannot run."])
    objectives(d, "sreehari")
    d.h("Evidence the Problem is Real")
    evidence_table(d, rf, ["Coastal sensing covers a long, exposed coastline.",
                           "Data gaps during storms have real human cost.",
                           ("Low-power long-range radio (LoRa) offers only about 0.3–50 kbps "
                            f"{rf('raza')}; marine links also suffer correlated (bursty) loss {rf('gilbert')}.",
                            "Sensor data must be compact and the receiver must cope with bursts of lost packets.")])
    d.h("Literature Survey")
    d.table([["#", "Author / Year", "Method used", "Result", "Limitation"],
             ["1", f"Al-Fuqaha et al., 2015 {rf('alfuqaha')}", "Survey of IoT technologies", "Protocols and architectures for sensors", "General, not marine"],
             ["2", f"Xu et al., 2019 {rf('xu')}", "Review of marine IoT monitoring", "Ocean sensing platforms and links", "Data loss handling not addressed"],
             ["3", f"Raza et al., 2017 {rf('raza')}", "LPWAN overview", "Range vs data rate trade-offs", "No recovery of lost data"],
             ["4", f"Augustin et al., 2016 {rf('lora')}", "LoRa measurements", "Long range at low throughput", "Duty-cycle limits"],
             ["5", f"Jouhari et al., 2019 {rf('jouhari')}", "Underwater sensor network survey", "Challenges of marine communication", "Underwater focus"],
             ["6", f"Gilbert, 1960 {rf('gilbert')}", "Two-state burst-noise channel", "Models clustered errors", "Theory only"],
             ["7", f"Elliott, 1963 {rf('elliott')}", "Error rates on burst channels", "Practical channel parameters", "Not for IoT telemetry"],
             ["8", f"Che et al., 2018 {rf('grud')}", "GRU-D with missing-value decay", "Better results with gaps", "Offline clinical data"],
             ["9", f"Cao et al., 2018 {rf('brits')}", "Bidirectional RNN imputation", "State-of-the-art gap filling", "Needs whole series; heavy"],
             ["10", f"Yoon et al., 2018 {rf('gain')}", "GAN-based imputation (GAIN)", "Imputes without full data", "Complex to train"],
             ["11", f"Lim & Zohren, 2021 {rf('limz')}", "Deep time-series forecasting survey", "Forecasting model families", "No real-time telemetry"],
             ["12", f"Holland, 1980 {rf('holland')}", "Hurricane pressure profile", "Realistic storm pressure field", "Needs storm parameters"],
             ["13", f"Chen et al., 2019 {rf('chenb')}", "CNN on satellite channels", "Intensity from imagery", "Large data and compute"],
             ["14", f"Denby & Lucia, 2020 {rf('denby')}", "Orbital edge computing", "Process data where captured", "Space segment only"],
             ["15", f"Shelby et al., 2014 {rf('coap')}", "CoAP for constrained devices", "Compact sensor messaging", "No gap recovery"]],
            [0.7, 3.4, 4.2, 4.4, 4.3], "Literature survey (15 articles)")
    d.p("**Gap:** imputation methods (GRU-D, BRITS, GAIN) work offline on complete datasets with heavy frameworks; "
        "marine IoT reviews describe links but not recovery; burst-loss channel models are rarely used to test "
        "sensor systems realistically. My part will generate realistic readings and loss, record the truth so "
        "recovery can be measured, recover lost readings online, and design low-cost nodes that send the same data.")
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
    d.table(ROLES, [4.2, 4.4, 8.4], "Team role split")
    d.p("**My role** is the beginning of the data path and its repair: what the sensors send, how it gets lost, and "
        "how we recover it.")
    timeline(d, [["1", "25–31 Aug", "Sensor-node simulator: readings, sequence numbers, configurable loss",
                  "Node sends JSON over UDP; LOST lines printed"],
                 ["2", "1–7 Sep", "Cyclone scenario (wind rises, pressure falls) and gap-filling baseline on the server",
                  "Missing sequence numbers are filled and marked"],
                 ["3", "8–14 Sep", "Integration test with gateway and server; hardware parts list", "Prototype shown at "
                  "Review 2; component list ready"]])
    video(d, VID1, "R1")
    rf.write(d)
    finish(d, f"{reg}_Sreehari_R1_Report")


# ============================================================================ R2 shared helpers
R2_RUN = ("To produce dated evidence for this report, the Review 2 prototype (repository commit `82bcb8a`, "
          "16/9/2026) was re-run unchanged with three sensor nodes for 60 seconds; the logs are in "
          "`docs/reports/evidence/r2_prototype/`. The team's original 12-second test reported 66 packets received, "
          "11 reconstructed and 2 critical, with overall risk 100 and the alert active.")


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
        "REST endpoints and an HTML dashboard (Figure 1).")
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
               "the prediction server succeeds (Figure 3)."])
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
    d.p(R2_RUN)
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
    d.table([["Choice", "Option", "Cost", "Ease of use", "Fit for our problem", "Decision"],
             ["Web framework", "Flask", "Free", "Very easy", "Sync by default; background thread needs care", ""],
             ["", "Django", "Free", "Heavy setup", "Too large for a small API", ""],
             ["", "**FastAPI**", "Free", "Easy", "Async + startup hooks for the UDP thread; automatic API docs", "Chosen"],
             ["Transport", "TCP", "—", "Easy", "Retransmissions hide the loss we must study; adds delay", ""],
             ["", "MQTT broker", "Free", "Extra service", "Good later; adds a broker to run", ""],
             ["", "**UDP datagrams**", "—", "Easy", "Loss is visible and measurable; matches lossy links", "Chosen"],
             ["Dashboard update", "**Polling 2 s**", "—", "Simplest", "Good enough for the prototype", "Chosen now"],
             ["", "WebSocket push", "—", "Moderate", "Lower latency; planned for the final system", "Next phase"]],
            [2.6, 2.6, 1.4, 2.2, 5.6, 2.6], "Comparison of alternatives for my module")
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
    contrib_placeholder(d)
    video(d, VID2, "R2")
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
    d.p("The gateway has two threads (Figure 1). The **receiver** reads UDP port 9001, decodes the record, classifies "
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
    d.p(R2_RUN)
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
    d.table([["Choice", "Option", "Accuracy / quality", "Compute & power", "Ease", "Decision"],
             ["Classifier", "**Threshold rule**", "Exact on breaches; no early warning", "Negligible", "Very easy", "Chosen now"],
             ["", "Logistic regression on trends", "Can warn before breach", "Very low", "Easy", "Next phase"],
             ["", "Deep network", "Possibly best", "High; needs GPU/data", "Hard", "Rejected"],
             ["Forwarding", "FIFO queue", "Critical waits behind others", "Low", "Easiest", "Rejected"],
             ["", "Fixed bandwidth cap per class", "Wastes capacity when idle", "Low", "Easy", "Rejected"],
             ["", "**Priority queue**", "Critical first, adapts instantly", "Low", "Easy", "Chosen"],
             ["Language", "**Python threads**", "Fast enough at our rates", "Runs on laptop / Pi", "Easy", "Chosen"]],
            [2.4, 3.6, 3.6, 2.8, 1.8, 2.8], "Comparison of alternatives for my module")
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
    contrib_placeholder(d)
    video(d, VID2, "R2")
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
        "reconstructed (Figure 1).")
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
               "interface is fixed."])
    d.code(["if random.random() < loss_rate:",
            "    print(f\"[{node_id}] seq={seq:05d} LOST (simulated link loss)\")",
            "else:",
            "    sock.sendto(encode(record), (HOST, SENSOR_TO_GATEWAY_PORT))",
            "",
            "def reconstruct_gap(node_id, prev_record, curr_record):",
            "    gap = curr_record[\"seq\"] - prev_record[\"seq\"]",
            "    for i in range(1, gap):",
            "        frac = i / gap      # linear interpolation for each variable"])
    d.p(R2_RUN)
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
    d.table([["Choice", "Option", "Approx. cost", "Realism / accuracy", "Power / ease", "Decision"],
             ["Data source", "**Simulated nodes**", "₹0", "Controllable, known truth", "Easiest", "Chosen now"],
             ["", "Recorded buoy archives", "₹0", "Real but no control over loss", "Needs data cleaning", "Later"],
             ["", "ESP32 hardware nodes", "≈₹800 / node", "Real sensors, real Wi-Fi loss", "Low power; build effort", "Next phase"],
             ["Gap filling", "Hold last value", "—", "Poor when values change fast", "Trivial", "Rejected"],
             ["", "**Linear interpolation**", "—", "Good baseline; needs next reading", "Easy", "Chosen now"],
             ["", "LSTM / GRU-D", "—", "Can learn dynamics", "Needs training", "Next phase"],
             ["Microcontroller", "Arduino Uno + ESP8266", "≈₹700", "Works", "Two boards", "Rejected"],
             ["", "**ESP32**", "≈₹400", "Wi-Fi built in", "Deep sleep available", "Planned"]],
            [2.6, 3.6, 2.2, 3.6, 2.6, 2.4], "Comparison of alternatives for my module")
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
    contrib_placeholder(d)
    video(d, VID2, "R2")
    finish(d, f"{reg}_Sreehari_R2_Report")


if __name__ == "__main__":
    for fn in (r1_laksh, r1_anvay, r1_sreehari, r2_laksh, r2_anvay, r2_sreehari):
        fn()
