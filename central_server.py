"""
Central Prediction Server
--------------------------
Receives QoS-prioritized telemetry from the edge gateway over UDP,
detects gaps caused by simulated packet loss, reconstructs missing
values from surrounding time-series context, computes a cyclone risk
score, and exposes everything through a FastAPI REST API + a simple
live HTML dashboard (spec sections 9.5, 9.6, 9.7).

Run:
    uvicorn central_server:app --reload --port 8000

The UDP listener thread starts automatically on FastAPI startup.
Then open http://127.0.0.1:8000 in a browser for the live dashboard.
"""
import socket
import threading
from collections import defaultdict, deque

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from common import HOST, GATEWAY_TO_SERVER_PORT, decode

HISTORY_LEN = 50
WIND_RISK_THRESHOLD = 60.0
PRESSURE_RISK_THRESHOLD = 990.0

telemetry_store = defaultdict(lambda: deque(maxlen=HISTORY_LEN))  # node -> recent records
last_seq = {}
stats = {"received": 0, "reconstructed": 0, "critical": 0}
lock = threading.Lock()


def reconstruct_gap(node_id, prev_record, curr_record):
    """
    Time-series recovery model (a simple, explainable stand-in for the
    LSTM described in the spec, section 9.5): linearly interpolate
    wind/temp/pressure across missing sequence numbers and mark each
    estimated record as reconstructed. Swap this function out for a
    trained LSTM/GRU model without changing the rest of the pipeline.
    """
    gap = curr_record["seq"] - prev_record["seq"]
    reconstructed = []
    for i in range(1, gap):
        frac = i / gap
        reconstructed.append({
            "node": node_id,
            "seq": prev_record["seq"] + i,
            "time": curr_record["time"],
            "wind": round(prev_record["wind"] + frac * (curr_record["wind"] - prev_record["wind"]), 2),
            "temp": round(prev_record["temp"] + frac * (curr_record["temp"] - prev_record["temp"]), 2),
            "pressure": round(prev_record["pressure"] + frac * (curr_record["pressure"] - prev_record["pressure"]), 2),
            "kind": "sensor",
            "traffic_class": curr_record.get("traffic_class", "NORMAL"),
            "reconstructed": True,
        })
    return reconstructed


def risk_score(record):
    """Simple cyclone-risk heuristic (0-100) combining wind + pressure."""
    wind_component = min(1.0, record["wind"] / WIND_RISK_THRESHOLD)
    pressure_component = min(1.0, max(0.0, (1013.0 - record["pressure"]) / (1013.0 - PRESSURE_RISK_THRESHOLD)))
    score = 100 * (0.6 * wind_component + 0.4 * pressure_component)
    return round(min(100.0, score), 1)


def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, GATEWAY_TO_SERVER_PORT))
    print(f"[server] listening for gateway traffic on {HOST}:{GATEWAY_TO_SERVER_PORT}")

    while True:
        data, _addr = sock.recvfrom(4096)
        record = decode(data)
        node_id = record["node"]

        with lock:
            stats["received"] += 1
            if record.get("traffic_class") == "CRITICAL":
                stats["critical"] += 1

            prev_seq = last_seq.get(node_id)
            if prev_seq is not None and record["seq"] - prev_seq > 1 and telemetry_store[node_id]:
                prev_record = telemetry_store[node_id][-1]
                filled = reconstruct_gap(node_id, prev_record, record)
                for rec in filled:
                    rec["risk"] = risk_score(rec)
                    telemetry_store[node_id].append(rec)
                    stats["reconstructed"] += 1
                print(f"[server] {node_id}: reconstructed {len(filled)} missing "
                      f"record(s) between seq {prev_seq} and {record['seq']}")

            record["risk"] = risk_score(record)
            telemetry_store[node_id].append(record)
            last_seq[node_id] = record["seq"]


# ----------------------------- FastAPI app ------------------------------
app = FastAPI(title="Cyclone Edge-Cloud Prediction Server")


@app.on_event("startup")
def start_listener():
    threading.Thread(target=udp_listener, daemon=True).start()


@app.get("/status")
def status():
    with lock:
        return {"stats": dict(stats), "nodes": list(telemetry_store.keys())}


@app.get("/telemetry/{node_id}")
def telemetry(node_id: str, limit: int = 20):
    with lock:
        records = list(telemetry_store.get(node_id, []))[-limit:]
    return {"node": node_id, "records": records}


@app.get("/predict")
def predict():
    """Latest reading per node + overall cyclone risk / alert state."""
    with lock:
        latest = {node_id: dq[-1] for node_id, dq in telemetry_store.items() if dq}
    if not latest:
        return {"overall_risk": 0, "alert": False, "nodes": {}}
    overall = max(rec["risk"] for rec in latest.values())
    return {"overall_risk": overall, "alert": overall >= 60, "nodes": latest}


DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Cyclone Monitoring Dashboard</title>
  <meta charset="utf-8">
  <style>
    body { font-family: Arial, sans-serif; background:#0b1220; color:#e6edf3; margin:2rem;}
    h1 { color:#7dd3fc; }
    table { border-collapse: collapse; width:100%; margin-top:1rem;}
    th, td { border:1px solid #223; padding:8px; text-align:center;}
    th { background:#132039;}
    .critical { color:#ff6b6b; font-weight:bold;}
    .reconstructed { color:#facc15; }
    #alert { padding:10px; margin-top:10px; border-radius:6px; }
    .alert-on { background:#7f1d1d; }
    .alert-off { background:#14532d; }
  </style>
</head>
<body>
  <h1>AI-Driven Edge-Cloud Cyclone Monitoring</h1>
  <div id="alert">Loading...</div>
  <table id="tbl">
    <thead><tr><th>Node</th><th>Seq</th><th>Wind</th><th>Temp</th><th>Pressure</th>
    <th>Risk</th><th>Class</th><th>Reconstructed</th></tr></thead>
    <tbody></tbody>
  </table>
  <script>
    async function refresh() {
      const res = await fetch('/predict');
      const data = await res.json();
      const alertDiv = document.getElementById('alert');
      alertDiv.className = data.alert ? 'alert-on' : 'alert-off';
      alertDiv.innerText = `Overall Risk: ${data.overall_risk} | Cyclone Alert: ${data.alert ? 'ACTIVE' : 'normal'}`;

      const tbody = document.querySelector('#tbl tbody');
      tbody.innerHTML = '';
      for (const [node, rec] of Object.entries(data.nodes || {})) {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${node}</td><td>${rec.seq}</td><td>${rec.wind}</td>
          <td>${rec.temp}</td><td>${rec.pressure}</td><td>${rec.risk}</td>
          <td class="${rec.traffic_class === 'CRITICAL' ? 'critical' : ''}">${rec.traffic_class}</td>
          <td class="${rec.reconstructed ? 'reconstructed' : ''}">${rec.reconstructed ? 'YES' : 'no'}</td>`;
        tbody.appendChild(row);
      }
    }
    setInterval(refresh, 2000);
    refresh();
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return DASHBOARD_HTML
