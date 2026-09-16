# AI-Driven Edge–Cloud Cyclone Prediction & Network Resilience — Prototype

A runnable Python simulation of the architecture in your project spec:

```
Sensor nodes (buoys/radars)  --UDP-->  Edge Gateway  --UDP-->  Central Prediction Server  --REST-->  Dashboard
   (lightweight telemetry)      (edge AI classify +      (gap reconstruction,
                                  AI-driven QoS)           risk scoring, API)
```

## Files
- `common.py` — shared telemetry format, QoS thresholds, encode/decode (spec 9.2, 9.4)
- `sensor_node.py` — simulates a buoy/radar/satellite station; sends UDP telemetry, drops packets randomly to emulate a lossy marine link, and worsens conditions after N seconds to simulate a developing cyclone (spec 9.2, 9.5)
- `edge_gateway.py` — receives sensor traffic, classifies it CRITICAL/NORMAL against cyclone thresholds ("edge AI"), and forwards it through a priority queue that reserves bandwidth for critical traffic during an alert ("AI-driven QoS") (spec 9.3, 9.4)
- `central_server.py` — FastAPI app: UDP listener detects sequence gaps and reconstructs missing values by interpolation (a stand-in for the LSTM model in spec 9.5 — swap in a trained model without touching the rest of the pipeline), computes a cyclone risk score, and serves REST endpoints + a live HTML dashboard (spec 9.6, 9.7)
- `requirements.txt` — `fastapi`, `uvicorn[standard]`

## Run it

Install dependencies:
```bash
pip install -r requirements.txt
```

Open **three terminals** (order matters — start the server first):

**Terminal 1 — central server (REST API + dashboard):**
```bash
uvicorn central_server:app --port 8000
```

**Terminal 2 — edge gateway:**
```bash
python3 edge_gateway.py
```

**Terminal 3+ — one or more sensor nodes:**
```bash
python3 sensor_node.py --node BUOY_07 --loss 0.15 --cyclone-after 15
python3 sensor_node.py --node RADAR_COAST_A --loss 0.1 --cyclone-after 25
```

Then open **http://127.0.0.1:8000** in a browser for the live dashboard, or query the API directly:

- `GET /predict` — latest reading per node + overall cyclone risk/alert
- `GET /status` — packet counters (received / reconstructed / critical)
- `GET /telemetry/{node_id}?limit=20` — recent history for one node

## What to watch for
1. Early on, everything is `NORMAL` traffic and risk stays low.
2. After `--cyclone-after` seconds, wind rises / pressure drops on a node → the gateway marks it `CRITICAL` and forwards it immediately, while it throttles `NORMAL` traffic from other nodes (visible in the gateway's console log and in `/predict`'s `alert` flag).
3. Whenever a sensor "loses" a packet (printed as `LOST` in its log), the central server detects the sequence gap and fills it in, marking the record `reconstructed: true` (visible in yellow on the dashboard, and counted in `/status`).

## Extending toward the full spec
This is a clean, minimal skeleton — each module maps to one spec section and can be upgraded independently:
- Swap UDP sockets for real **MQTT/CoAP** (e.g. `paho-mqtt`, `aiocoap`).
- Replace `classify_traffic()`'s threshold rule with a trained **ML/RL QoS policy**.
- Replace `reconstruct_gap()`'s linear interpolation with a trained **LSTM** (e.g. PyTorch/TensorFlow) over each node's time-series window.
- Replace the simulated buoy imagery step with real **edge AI feature extraction** on satellite imagery, forwarding only the compact features/risk flags.
- Run the topology in **Mininet** instead of loopback sockets for a true multi-tier WAN emulation.
- Add a WebSocket endpoint to `central_server.py` for push updates instead of the dashboard's polling.

Note: this code demonstrates the *mechanism* described in your spec (edge classification, AI-driven QoS, packet-loss reconstruction, prediction API). It is not a verified, evaluated system — the "AI" pieces (classification thresholds, interpolation) are simple, explainable placeholders you should replace with the trained models described in your report once you have data to train on.
# AI-DRIVEN-EDGE-CLOUD-NETWORK
