"""
Shared utilities and constants for the AI-Driven Edge-Cloud Cyclone
Prediction & Network Resilience simulation.

Maps to spec section 9.2 (lightweight telemetry) and 9.4 (AI-driven QoS).
"""
import json
import time

# ---- Network configuration --------------------------------------------
HOST = "127.0.0.1"
SENSOR_TO_GATEWAY_PORT = 9001      # sensors -> edge gateway
GATEWAY_TO_SERVER_PORT = 9002      # edge gateway -> central prediction server

# ---- Cyclone risk thresholds (drive AI-driven QoS classification) -----
WIND_CRITICAL_THRESHOLD = 60.0       # km/h
PRESSURE_CRITICAL_THRESHOLD = 990.0  # hPa

TRAFFIC_CRITICAL = "CRITICAL"
TRAFFIC_NORMAL = "NORMAL"


def make_telemetry(node_id, seq, wind, temp, pressure, kind="sensor"):
    """Compact telemetry record, matching the example in spec section 9.2."""
    return {
        "node": node_id,
        "seq": seq,
        "time": time.strftime("%H:%M:%S"),
        "wind": round(wind, 2),
        "temp": round(temp, 2),
        "pressure": round(pressure, 2),
        "kind": kind,          # "sensor" or "edge_feature"
        "reconstructed": False,
    }


def classify_traffic(record):
    """AI/threshold-driven QoS classification (spec section 9.4)."""
    if record["wind"] >= WIND_CRITICAL_THRESHOLD or record["pressure"] <= PRESSURE_CRITICAL_THRESHOLD:
        return TRAFFIC_CRITICAL
    return TRAFFIC_NORMAL


def encode(record):
    return json.dumps(record).encode("utf-8")


def decode(data):
    return json.loads(data.decode("utf-8"))
