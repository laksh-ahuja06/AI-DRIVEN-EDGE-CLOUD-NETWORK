"""
Shared utilities and constants for the AI-Driven Edge-Cloud Cyclone
Prediction & Network Resilience system.

Maps to spec section 9.2 (lightweight telemetry), 9.4 (AI-driven QoS)
and FIG. 5 (input -> parse/validate -> AI inference -> QoS action).

Every host/port can be overridden with an environment variable so the
same code runs on one laptop (loopback), across a college LAN (ESP32
hardware nodes, Raspberry Pi gateway) or inside Mininet.
"""
import json
import os
import time

# ---- Network configuration --------------------------------------------
BIND_HOST = os.environ.get("BIND_HOST", "0.0.0.0")           # listeners bind here
GATEWAY_HOST = os.environ.get("GATEWAY_HOST", "127.0.0.1")   # where sensors send
SERVER_HOST = os.environ.get("SERVER_HOST", "127.0.0.1")     # where the gateway forwards
HOST = GATEWAY_HOST  # backwards-compatible alias used by the original scripts

SENSOR_TO_GATEWAY_PORT = int(os.environ.get("SENSOR_TO_GATEWAY_PORT", 9001))  # sensors -> edge gateway
GATEWAY_TO_SERVER_PORT = int(os.environ.get("GATEWAY_TO_SERVER_PORT", 9002))  # gateway -> central server
GATEWAY_CONTROL_PORT = int(os.environ.get("GATEWAY_CONTROL_PORT", 9003))      # server -> gateway QoS feedback
NODE_ALERT_PORT = int(os.environ.get("NODE_ALERT_PORT", 9004))                # gateway -> hardware node alerts

# ---- Cyclone risk thresholds (drive AI-driven QoS classification) -----
WIND_CRITICAL_THRESHOLD = 60.0       # km/h
PRESSURE_CRITICAL_THRESHOLD = 990.0  # hPa

# ---- Traffic classes (spec 11.3 step 22: critical / normal / non-essential)
TRAFFIC_CRITICAL = "CRITICAL"
TRAFFIC_NORMAL = "NORMAL"
TRAFFIC_NON_ESSENTIAL = "NON_ESSENTIAL"
TRAFFIC_CLASSES = (TRAFFIC_CRITICAL, TRAFFIC_NORMAL, TRAFFIC_NON_ESSENTIAL)

# ---- Message kinds -----------------------------------------------------
KIND_SENSOR = "sensor"              # buoy / radar telemetry
KIND_EDGE_FEATURE = "edge_feature"  # satellite ground station edge-AI output
KIND_HOUSEKEEPING = "housekeeping"  # battery / diagnostics (non-essential)
KIND_GATEWAY_STATS = "gateway_stats"

SENSOR_FIELDS = ("wind", "temp", "pressure")

# Physically plausible ranges used by validate() to reject corrupt packets.
VALID_RANGES = {
    "wind": (0.0, 400.0),
    "temp": (-10.0, 50.0),
    "pressure": (850.0, 1090.0),
}


def make_telemetry(node_id, seq, wind, temp, pressure, kind=KIND_SENSOR):
    """Compact telemetry record, matching the example in spec section 9.2."""
    return {
        "node": node_id,
        "seq": seq,
        "time": time.strftime("%H:%M:%S"),
        "t_sent": round(time.time(), 3),
        "wind": round(wind, 2),
        "temp": round(temp, 2),
        "pressure": round(pressure, 2),
        "kind": kind,
        "reconstructed": False,
    }


def make_housekeeping(node_id, seq, battery_v, rssi):
    """Low-value diagnostics message: the first thing QoS drops under an alert."""
    return {
        "node": node_id,
        "seq": seq,
        "time": time.strftime("%H:%M:%S"),
        "t_sent": round(time.time(), 3),
        "kind": KIND_HOUSEKEEPING,
        "battery_v": round(battery_v, 2),
        "rssi": int(rssi),
    }


class ValidationError(ValueError):
    pass


def validate(record):
    """
    Parse/validate step (FIG. 5, spec 11.3 step 20). Raises ValidationError
    for anything a downstream stage could not safely use. Returns the
    record with numeric fields coerced to float.
    """
    if not isinstance(record, dict):
        raise ValidationError("record is not a JSON object")
    node = record.get("node")
    if not isinstance(node, str) or not node or len(node) > 32:
        raise ValidationError("missing or invalid 'node'")
    seq = record.get("seq")
    if not isinstance(seq, int) or isinstance(seq, bool) or seq < 0:
        raise ValidationError("missing or invalid 'seq'")

    kind = record.setdefault("kind", KIND_SENSOR)
    if kind == KIND_SENSOR:
        for field in SENSOR_FIELDS:
            value = record.get(field)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValidationError(f"missing or non-numeric '{field}'")
            lo, hi = VALID_RANGES[field]
            if not lo <= value <= hi:
                raise ValidationError(f"'{field}'={value} outside physical range [{lo}, {hi}]")
            record[field] = float(value)
    elif kind == KIND_EDGE_FEATURE:
        risk = record.get("sat_risk")
        if not isinstance(risk, (int, float)) or not 0.0 <= risk <= 100.0:
            raise ValidationError("edge_feature needs 'sat_risk' in [0, 100]")
    elif kind not in (KIND_HOUSEKEEPING, KIND_GATEWAY_STATS):
        raise ValidationError(f"unknown kind '{kind}'")
    return record


def classify_traffic(record):
    """Rule-based QoS classification baseline (spec section 9.4)."""
    kind = record.get("kind", KIND_SENSOR)
    if kind == KIND_HOUSEKEEPING:
        return TRAFFIC_NON_ESSENTIAL
    if kind == KIND_EDGE_FEATURE:
        return TRAFFIC_CRITICAL if record.get("risk_flag") else TRAFFIC_NORMAL
    if record["wind"] >= WIND_CRITICAL_THRESHOLD or record["pressure"] <= PRESSURE_CRITICAL_THRESHOLD:
        return TRAFFIC_CRITICAL
    return TRAFFIC_NORMAL


def encode(record):
    return json.dumps(record, separators=(",", ":")).encode("utf-8")


def decode(data):
    return json.loads(data.decode("utf-8"))
