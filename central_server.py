"""
Central Prediction Server
--------------------------
Receives QoS-prioritised traffic from the edge gateway over UDP and:

  * validates each record and tracks sequence numbers per node;
  * repairs gaps caused by packet loss with the LSTM reconstructor
    (linear interpolation if no trained model is present) - spec 9.5;
  * publishes provisional LSTM forecasts for overdue packets in real time
    and replaces them when the real data / gap repair arrives;
  * accepts late packets and swaps them in for their reconstructed copies;
  * fuses buoy/radar risk with satellite edge-AI risk into one cyclone-risk
    output and a short-term forecast - spec 9.6;
  * sends QoS feedback (alert on/off) back to the gateway - FIG. 8;
  * serves REST endpoints, a WebSocket stream and a live dashboard - spec 9.7.

Run:
    uvicorn central_server:app --port 8000
    RECON_METHOD=linear uvicorn central_server:app --port 8000   # baseline

Then open http://127.0.0.1:8000
"""
import asyncio
import os
import socket
import threading
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from common import (
    BIND_HOST,
    GATEWAY_CONTROL_PORT,
    GATEWAY_HOST,
    GATEWAY_TO_SERVER_PORT,
    KIND_EDGE_FEATURE,
    KIND_GATEWAY_STATS,
    KIND_HOUSEKEEPING,
    KIND_SENSOR,
    PRESSURE_CRITICAL_THRESHOLD,
    TRAFFIC_CLASSES,
    WIND_CRITICAL_THRESHOLD,
    ValidationError,
    decode,
    encode,
    validate,
)
from reconstruction import MIN_HISTORY, Reconstructor

HISTORY_LEN = 200
MAX_GAP = 30                # longer outages are not reconstructed (node probably restarted)
MAX_PROVISIONAL = 5         # real-time forecasts per node before we stop guessing
OVERDUE_FACTOR = 2.5        # packet is overdue after 2.5x the node's usual interval
ALERT_ON, ALERT_OFF = 60.0, 50.0
FORECAST_STEPS = 10
WIND_RISK_THRESHOLD = WIND_CRITICAL_THRESHOLD
PRESSURE_RISK_THRESHOLD = PRESSURE_CRITICAL_THRESHOLD
DASHBOARD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.html")


def risk_score(record, pressure_tendency=0.0):
    """
    Explainable cyclone-risk heuristic (0-100):
      50% wind relative to the 60 km/h threshold,
      35% pressure depression towards 990 hPa,
      15% pressure tendency (falling >= 1 hPa per reading counts fully).
    """
    wind_c = min(1.0, record["wind"] / WIND_RISK_THRESHOLD)
    pres_c = min(1.0, max(0.0, (1013.0 - record["pressure"]) / (1013.0 - PRESSURE_RISK_THRESHOLD)))
    tend_c = min(1.0, max(0.0, -pressure_tendency))
    return round(min(100.0, 100 * (0.5 * wind_c + 0.35 * pres_c + 0.15 * tend_c)), 1)


class NodeState:
    def __init__(self):
        self.records = deque(maxlen=HISTORY_LEN)
        self.last_seq = None
        self.last_arrival = None
        self.interval = None       # EMA of inter-arrival time (s)


class ServerState:
    def __init__(self, recon_method="lstm"):
        self.lock = threading.Lock()
        self.recon = Reconstructor(recon_method)
        self.nodes = defaultdict(NodeState)
        self.satellite = defaultdict(lambda: deque(maxlen=50))
        self.housekeeping = {}
        self.gateway = {}
        self.latency = {c: deque(maxlen=300) for c in TRAFFIC_CLASSES}
        self.stats = {"received": 0, "reconstructed": 0, "concealed": 0, "late_recovered": 0,
                      "duplicates": 0, "invalid": 0, "critical": 0, "housekeeping": 0,
                      "sat_frames": 0, "sat_raw_bytes": 0, "sat_sent_bytes": 0, "sat_zlib_bytes": 0}
        self.alert = False
        self.alert_changed = threading.Event()

    # ------------------------------------------------------------ helpers
    @staticmethod
    def _values(records):
        return [(r["wind"], r["temp"], r["pressure"]) for r in records if not r.get("provisional")]

    @staticmethod
    def _tendency(records, n=5):
        vals = [r["pressure"] for r in list(records)[-n:] if not r.get("provisional")]
        return (vals[-1] - vals[0]) / (len(vals) - 1) if len(vals) >= 2 else 0.0

    def _make_estimate(self, node_id, seq, values, template, method, provisional=False):
        wind, temp, pres = (round(float(v), 2) for v in values)
        return {"node": node_id, "seq": seq, "time": template.get("time"), "wind": wind, "temp": temp,
                "pressure": pres, "kind": KIND_SENSOR, "traffic_class": template.get("traffic_class", "NORMAL"),
                "reconstructed": True, "provisional": provisional, "method": method}

    def _append(self, node, rec):
        rec["risk"] = risk_score(rec, self._tendency(list(node.records) + [rec]))
        node.records.append(rec)

    # ------------------------------------------------------------ ingest
    def ingest(self, record, now=None):
        """Process one decoded datagram. Returns a short status string (useful for tests/logs)."""
        now = time.time() if now is None else now
        try:
            record = validate(record)
        except ValidationError:
            with self.lock:
                self.stats["invalid"] += 1
            return "invalid"

        kind = record.get("kind", KIND_SENSOR)
        with self.lock:
            cls = record.get("traffic_class")
            if cls in self.latency and "t_gw" in record:
                self.latency[cls].append(max(0.0, now - record["t_gw"]))
            if kind == KIND_GATEWAY_STATS:
                self.gateway = record
                return "gateway_stats"
            self.stats["received"] += 1
            if cls == "CRITICAL":
                self.stats["critical"] += 1
            if kind == KIND_HOUSEKEEPING:
                self.stats["housekeeping"] += 1
                self.housekeeping[record["node"]] = record
                return "housekeeping"
            if kind == KIND_EDGE_FEATURE:
                self.satellite[record["node"]].append(record)
                self.stats["sat_frames"] += 1
                self.stats["sat_raw_bytes"] += int(record.get("raw_bytes", 0))
                self.stats["sat_sent_bytes"] += int(record.get("sent_bytes", 0))
                self.stats["sat_zlib_bytes"] += int(record.get("zlib_bytes", 0))
                return "edge_feature"
            return self._ingest_sensor(record, now)

    def _ingest_sensor(self, record, now):
        node_id, seq = record["node"], record["seq"]
        node = self.nodes[node_id]
        record.setdefault("reconstructed", False)

        if node.last_seq is not None and seq <= node.last_seq:
            if seq == 1 or node.last_seq - seq > 50:     # node rebooted: start a fresh stream
                self.nodes[node_id] = node = NodeState()
            else:
                for i, old in enumerate(node.records):
                    if old["seq"] == seq:
                        if old.get("reconstructed") and not old.get("provisional"):
                            record["late_recovered"] = True
                            record["risk"] = risk_score(record, self._tendency(list(node.records)[:i + 1]))
                            node.records[i] = record
                            self.stats["late_recovered"] += 1
                            return "late_recovered"
                        break
                self.stats["duplicates"] += 1
                return "duplicate"

        # Drop provisional real-time forecasts; real data / a proper repair replaces them.
        while node.records and node.records[-1].get("provisional"):
            node.records.pop()

        status = "ok"
        if node.last_seq is not None and node.records:
            gap = seq - node.last_seq - 1
            if 0 < gap <= MAX_GAP:
                history = self._values(node.records)
                filled = self.recon.fill_gap(history, (record["wind"], record["temp"], record["pressure"]), gap)
                for k, values in enumerate(filled, start=1):
                    self._append(node, self._make_estimate(node_id, node.last_seq + k, values, record,
                                                           self.recon.method))
                self.stats["reconstructed"] += gap
                status = f"reconstructed {gap}"
            elif gap > MAX_GAP:
                status = f"outage of {gap} readings not reconstructed"

        if node.last_arrival is not None:
            dt = now - node.last_arrival
            if 0 < dt < 60:
                node.interval = dt if node.interval is None else 0.8 * node.interval + 0.2 * dt
        node.last_arrival = now
        node.last_seq = seq
        self._append(node, record)
        return status

    # ------------------------------------------------------------ real-time concealment
    def conceal_overdue(self, now=None):
        """Publish provisional forecasts for nodes whose next packet is overdue."""
        now = time.time() if now is None else now
        added = 0
        with self.lock:
            for node_id, node in self.nodes.items():
                if node.interval is None or node.last_arrival is None or not node.records:
                    continue
                provisional = sum(1 for r in node.records if r.get("provisional"))
                if provisional >= MAX_PROVISIONAL:
                    continue
                if now - node.last_arrival < (OVERDUE_FACTOR + provisional) * node.interval:
                    continue
                history = self._values(node.records)
                if len(history) < MIN_HISTORY:
                    continue
                values = self.recon.forecast(history, provisional + 1)[-1]
                method = "lstm-forecast" if self.recon.method == "lstm" else "hold-last"
                est = self._make_estimate(node_id, node.last_seq + provisional + 1, values, node.records[-1],
                                          method, provisional=True)
                self._append(node, est)
                self.stats["concealed"] += 1
                added += 1
        return added

    # ------------------------------------------------------------ prediction
    def predict(self):
        with self.lock:
            latest = {nid: dict(n.records[-1]) for nid, n in self.nodes.items() if n.records}
            histories = {nid: self._values(n.records) for nid, n in self.nodes.items()}
            sats = {sid: {k: v for k, v in dq[-1].items() if k != "thumb"} for sid, dq in self.satellite.items() if dq}

        forecasts = {}
        for nid, hist in histories.items():
            if len(hist) >= MIN_HISTORY:
                fc = self.recon.forecast(hist, FORECAST_STEPS)
                peak = max(risk_score({"wind": w, "pressure": p}) for w, _t, p in fc)
                forecasts[nid] = {"steps": FORECAST_STEPS, "peak_risk": peak,
                                  "wind": [round(float(w), 1) for w, _t, _p in fc],
                                  "pressure": [round(float(p), 1) for _w, _t, p in fc]}

        node_risk = max((r["risk"] for r in latest.values()), default=0.0)
        sat_risk = max((s.get("sat_risk", 0.0) for s in sats.values()), default=0.0)
        forecast_risk = max((f["peak_risk"] for f in forecasts.values()), default=0.0)
        # Fusion: in-situ observations dominate; satellite and forecast can raise the risk early.
        overall = round(max(node_risk, 0.9 * sat_risk, 0.8 * forecast_risk), 1)

        with self.lock:
            prev = self.alert
            if not self.alert and overall >= ALERT_ON:
                self.alert = True
            elif self.alert and overall < ALERT_OFF:
                self.alert = False
            if self.alert != prev:
                self.alert_changed.set()
            alert = self.alert
        return {"overall_risk": overall, "alert": alert,
                "components": {"in_situ": node_risk, "satellite": sat_risk, "forecast": forecast_risk},
                "nodes": latest, "satellite": sats, "forecast": forecasts, "reconstruction": self.recon.method}

    def metrics(self):
        with self.lock:
            lat = {}
            for cls, dq in self.latency.items():
                vals = sorted(dq)
                lat[cls] = {"n": len(vals),
                            "avg_ms": round(1000 * sum(vals) / len(vals), 1) if vals else None,
                            "p95_ms": round(1000 * vals[int(0.95 * (len(vals) - 1))], 1) if vals else None}
            s = dict(self.stats)
        raw, sent = s["sat_raw_bytes"], s["sat_sent_bytes"]
        sensor_total = s["received"] - s["housekeeping"] - s["sat_frames"]
        return {
            "latency_gateway_to_server": lat,
            "bandwidth": {"sat_raw_bytes": raw, "sat_sent_bytes": sent, "sat_zlib_bytes": s["sat_zlib_bytes"],
                          "reduction_pct": round(100 * (1 - sent / raw), 3) if raw else None,
                          "reduction_vs_zlib_pct": round(100 * (1 - sent / s["sat_zlib_bytes"]), 3)
                          if s["sat_zlib_bytes"] else None},
            "recovery": {"sensor_packets": sensor_total, "reconstructed": s["reconstructed"],
                         "concealed_realtime": s["concealed"], "late_recovered": s["late_recovered"],
                         "method": self.recon.method},
        }

    def snapshot(self, history=60):
        pred = self.predict()
        with self.lock:
            series = {nid: [{k: r.get(k) for k in ("seq", "wind", "pressure", "temp", "risk",
                                                   "reconstructed", "provisional", "traffic_class")}
                            for r in list(n.records)[-history:]] for nid, n in self.nodes.items()}
            sat_full = {sid: dq[-1] for sid, dq in self.satellite.items() if dq}
            gw = dict(self.gateway)
            stats = dict(self.stats)
            hk = dict(self.housekeeping)
        pred["satellite"] = sat_full
        return {**pred, "series": series, "gateway": gw, "stats": stats, "housekeeping": hk,
                "metrics": self.metrics(), "server_time": time.strftime("%H:%M:%S")}


STATE = ServerState(os.environ.get("RECON_METHOD", "lstm"))


# ----------------------------------------------------------------- network threads
def udp_listener(state=STATE, bind_host=BIND_HOST, port=GATEWAY_TO_SERVER_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((bind_host, port))
    print(f"[server] listening for gateway traffic on {bind_host}:{port} "
          f"(reconstruction={state.recon.method})", flush=True)
    while True:
        data, _addr = sock.recvfrom(65535)
        try:
            record = decode(data)
        except ValueError:
            with state.lock:
                state.stats["invalid"] += 1
            continue
        status = state.ingest(record)
        if status.startswith("reconstructed") or status == "late_recovered":
            print(f"[server] {record.get('node')}: {status} (seq {record.get('seq')})", flush=True)


def background_loop(state=STATE, gateway_addr=(GATEWAY_HOST, GATEWAY_CONTROL_PORT)):
    """Real-time concealment + periodic risk evaluation + QoS feedback to the gateway."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    last_feedback = 0.0
    while True:
        time.sleep(0.25)
        state.conceal_overdue()
        now = time.time()
        if now - last_feedback >= 2.0 or state.alert_changed.is_set():
            pred = state.predict()
            state.alert_changed.clear()
            try:
                sock.sendto(encode({"type": "qos_feedback", "alert": pred["alert"], "risk": pred["overall_risk"]}),
                            gateway_addr)
            except OSError:
                pass
            last_feedback = now


# ----------------------------------------------------------------- FastAPI app
@asynccontextmanager
async def lifespan(_app):
    if os.environ.get("SERVER_START_THREADS", "1") == "1":
        threading.Thread(target=udp_listener, daemon=True).start()
        threading.Thread(target=background_loop, daemon=True).start()
    yield


app = FastAPI(title="Cyclone Edge-Cloud Prediction Server", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
def dashboard():
    with open(DASHBOARD_PATH, encoding="utf-8") as f:
        return f.read()


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/predict")
def predict():
    """Latest reading per node, fused cyclone risk, alert state and 10-step forecast."""
    return STATE.predict()


@app.get("/snapshot")
def snapshot():
    """Everything the dashboard shows (same payload as the WebSocket stream)."""
    return STATE.snapshot()


@app.get("/status")
def status():
    with STATE.lock:
        return {"stats": dict(STATE.stats), "nodes": list(STATE.nodes.keys()),
                "satellite_stations": list(STATE.satellite.keys()), "alert": STATE.alert}


@app.get("/telemetry/{node_id}")
def telemetry(node_id: str, limit: int = 20):
    with STATE.lock:
        node = STATE.nodes.get(node_id)
        records = list(node.records)[-limit:] if node else []
    return {"node": node_id, "records": records}


@app.get("/satellite")
def satellite():
    with STATE.lock:
        return {sid: list(dq)[-1] for sid, dq in STATE.satellite.items() if dq}


@app.get("/gateway")
def gateway():
    with STATE.lock:
        return dict(STATE.gateway)


@app.get("/metrics")
def metrics():
    return STATE.metrics()


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(STATE.snapshot())
            await asyncio.sleep(1.0)
    except (WebSocketDisconnect, RuntimeError):
        pass
