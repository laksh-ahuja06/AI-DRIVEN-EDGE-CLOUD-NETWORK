import json

import numpy as np
import pytest

from common import (TRAFFIC_CRITICAL, TRAFFIC_NON_ESSENTIAL, TRAFFIC_NORMAL, ValidationError, classify_traffic,
                    encode, make_housekeeping, make_telemetry, validate)
from edge_ai import QoSClassifier, extract_features, trend_features
from lstm import LSTMRegressor
from ocean_model import CycloneParams, GilbertElliottLink, OceanNode
from qos import QoSScheduler
from reconstruction import Reconstructor, linear_fill
from satellite_station import SyntheticImager


# ------------------------------------------------------------------ common
def test_validate_accepts_spec_example():
    rec = {"node": "BUOY_07", "time": "12:05:10", "wind": 42.1, "temp": 28.4, "pressure": 982.6, "seq": 1842}
    assert validate(rec)["kind"] == "sensor"


@pytest.mark.parametrize("bad", [
    {"seq": 1, "wind": 1, "temp": 1, "pressure": 1000},                      # no node
    {"node": "B", "seq": -1, "wind": 1, "temp": 1, "pressure": 1000},        # bad seq
    {"node": "B", "seq": 1, "wind": "x", "temp": 1, "pressure": 1000},       # non-numeric
    {"node": "B", "seq": 1, "wind": 10, "temp": 1, "pressure": 5},           # impossible pressure
    {"node": "B", "seq": 1, "kind": "edge_feature"},                         # missing sat_risk
    "not a dict",
])
def test_validate_rejects_bad_packets(bad):
    with pytest.raises(ValidationError):
        validate(bad)


def test_rule_classifier_three_classes():
    assert classify_traffic(make_telemetry("B", 1, 70, 28, 1000)) == TRAFFIC_CRITICAL
    assert classify_traffic(make_telemetry("B", 1, 20, 28, 985)) == TRAFFIC_CRITICAL
    assert classify_traffic(make_telemetry("B", 1, 20, 28, 1008)) == TRAFFIC_NORMAL
    assert classify_traffic(make_housekeeping("B", 1, 3.7, -70)) == TRAFFIC_NON_ESSENTIAL


# ------------------------------------------------------------------ ocean model
def test_cyclone_raises_wind_and_drops_pressure():
    node = OceanNode(CycloneParams(onset_step=10, speed_km_per_step=10, closest_km=10), seed=1)
    tr = np.array(node.trace(120))
    calm, storm = tr[:10], tr[50:80]
    assert storm[:, 0].max() > 60 > calm[:, 0].max()
    assert storm[:, 2].min() < 990 < calm[:, 2].min()


def test_gilbert_elliott_mean_loss():
    link = GilbertElliottLink(0.1, burstiness=0.7, seed=0)
    rate = np.mean([link.lost() for _ in range(50000)])
    assert 0.08 < rate < 0.12


# ------------------------------------------------------------------ edge AI
def test_satellite_features_track_intensity_and_compress():
    imager = SyntheticImager(size=256, seed=0)
    calm = extract_features(imager.frame(0.0))
    storm = extract_features(imager.frame(1.0))
    assert calm["sat_risk"] < 10 and not calm["risk_flag"]
    assert storm["sat_risk"] > 60 and storm["risk_flag"]
    assert len(encode(storm)) < 0.01 * imager.frame(1.0).nbytes


def test_qos_classifier_learns_simple_rule():
    rng = np.random.default_rng(0)
    X = np.array([trend_features([(w, 28, 1008 - w / 5)]) for w in rng.uniform(0, 100, 500)])
    y = (X[:, 0] > 55).astype(float)
    clf = QoSClassifier().fit(X, y, epochs=600)
    assert (clf.predict(X) == (y > 0.5)).mean() > 0.95


# ------------------------------------------------------------------ LSTM
def test_lstm_gradients_match_numerical():
    m = LSTMRegressor(3, 5, 2, seed=1)
    rng = np.random.default_rng(0)
    X, Y = rng.normal(size=(4, 6, 3)), rng.normal(size=(4, 2))
    _, grads = m.loss_and_grads(X, Y)
    for key in m.params:
        p = m.params[key]
        idx = tuple(rng.integers(0, s) for s in p.shape)
        old = p[idx]
        p[idx] = old + 1e-6
        lp, _ = m.loss_and_grads(X, Y)
        p[idx] = old - 1e-6
        lm, _ = m.loss_and_grads(X, Y)
        p[idx] = old
        num = (lp - lm) / 2e-6
        assert abs(num - grads[key][idx]) <= 1e-5 * max(1.0, abs(num))


def test_lstm_learns_a_sine_wave():
    t = np.arange(400) * 0.3
    s = np.sin(t)
    X = np.array([s[i:i + 10, None] for i in range(380)])
    Y = s[10:390, None]
    m = LSTMRegressor(1, 12, 1, seed=0)
    m.fit(X, Y, epochs=30, batch_size=32, lr=1e-2, verbose=False)
    assert ((m.forward(X) - Y) ** 2).mean() < 0.01


def test_reconstruction_fills_gap_and_hits_anchor():
    rec = Reconstructor("lstm")
    hist = [(15 + i, 28.0, 1008 - 0.5 * i) for i in range(15)]
    nxt = (15 + 18, 28.0, 1008 - 0.5 * 18)
    fill = rec.fill_gap(hist, nxt, 3)
    assert fill.shape == (3, 3)
    # Between the endpoints and close to the straight line for a linear trend.
    assert np.abs(fill - linear_fill(hist[-1], nxt, 3)).max() < 3.0


# ------------------------------------------------------------------ QoS scheduler
def _run(sched, arrivals, until):
    out, now = [], 0.0
    arrivals = sorted(arrivals)
    i = 0
    while now < until:
        while i < len(arrivals) and arrivals[i][0] <= now:
            t, cls, size = arrivals[i]
            sched.enqueue((t, cls), cls, size, now)
            i += 1
        item = sched.dequeue(now)
        if item:
            (t, cls), _, _ = item
            out.append((cls, now - t))
        else:
            now += 0.005
    return out


def test_priority_beats_fifo_for_critical_under_congestion():
    arrivals = [(k * 0.1, TRAFFIC_NORMAL, 300) for k in range(200)]          # 3000 B/s offered
    arrivals += [(5 + k, TRAFFIC_CRITICAL, 300) for k in range(10)]
    lat = {}
    for policy in ("fifo", "priority"):
        sched = QoSScheduler(rate_bps=1500, policy=policy, max_queue=1000)
        sent = _run(sched, arrivals, 60)
        lat[policy] = max(d for c, d in sent if c == TRAFFIC_CRITICAL)
    assert lat["priority"] < 0.5 < lat["fifo"]


def test_alert_sheds_non_essential_only_when_congested():
    sched = QoSScheduler(rate_bps=1000, policy="priority")
    sched.set_alert(True)
    assert sched.enqueue("hk", TRAFFIC_NON_ESSENTIAL, 100, 0.0)              # idle link: keep it
    for _ in range(20):
        sched.enqueue("n", TRAFFIC_NORMAL, 300, 0.0)                         # build a backlog
    assert not sched.enqueue("hk", TRAFFIC_NON_ESSENTIAL, 100, 0.0)
    assert sched.stats[TRAFFIC_NON_ESSENTIAL].shed == 1


def test_next_ready_in_is_consistent_with_dequeue():
    sched = QoSScheduler(rate_bps=1000, policy="priority", burst_bytes=3000)
    for k in range(30):
        sched.enqueue(k, TRAFFIC_NORMAL if k % 3 else TRAFFIC_NON_ESSENTIAL, 400, 0.0)
    sched.set_alert(True)  # alert while a backlog exists: the critical reserve applies
    now, sent = 0.0, 0
    for _ in range(200):
        wait = sched.next_ready_in(now)
        if wait is None:
            break
        now += wait + 1e-9
        assert sched.dequeue(now) is not None
        sent += 1
    assert sent == 30


# ------------------------------------------------------------------ gateway
def test_gateway_classifies_and_drops_invalid():
    from edge_gateway import Gateway
    gw = Gateway(policy="rule", verbose=False)
    assert gw.handle_packet(b"{not json") is None
    assert gw.handle_packet(encode({"node": "B", "seq": 1, "wind": 10, "temp": 28, "pressure": 3})) is None
    rec = gw.handle_packet(encode(make_telemetry("B", 1, 80, 28, 1000)))
    assert rec["traffic_class"] == TRAFFIC_CRITICAL and gw.alert
    assert gw.invalid == 2


def test_gateway_ml_policy_flags_early():
    from edge_gateway import Gateway
    gw = Gateway(policy="hybrid", verbose=False)
    if gw.clf is None:
        pytest.skip("trained QoS model not present")
    # Pressure falling fast and wind climbing, but both still below the thresholds.
    classes = []
    for k in range(6):
        rec = gw.handle_packet(encode(make_telemetry("B", k + 1, 30 + 5 * k, 28, 1006 - 2.5 * k)))
        classes.append(rec["traffic_class"])
    assert classify_traffic(rec) == TRAFFIC_NORMAL
    assert classes[-1] == TRAFFIC_CRITICAL


# ------------------------------------------------------------------ server
@pytest.fixture
def state():
    from central_server import ServerState
    return ServerState("lstm")


def _send(state, seq, wind=20.0, pressure=1008.0, now=None, node="BUOY_07"):
    rec = make_telemetry(node, seq, wind, 28.0, pressure)
    rec["traffic_class"] = classify_traffic(rec)
    return state.ingest(json.loads(json.dumps(rec)), now=now if now is not None else float(seq))


def test_server_reconstructs_gap(state):
    for s in range(1, 8):
        _send(state, s, wind=20 + s)
    assert _send(state, 11, wind=31) == "reconstructed 3"
    recs = list(state.nodes["BUOY_07"].records)
    assert [r["seq"] for r in recs] == list(range(1, 12))
    assert all(r["reconstructed"] for r in recs[7:10])
    assert state.stats["reconstructed"] == 3


def test_server_late_packet_replaces_estimate(state):
    for s in (1, 2, 3, 4, 5, 7):
        _send(state, s)
    assert _send(state, 6, wind=22.2) == "late_recovered"
    rec6 = [r for r in state.nodes["BUOY_07"].records if r["seq"] == 6][0]
    assert not rec6["reconstructed"] and rec6["wind"] == 22.2
    assert _send(state, 6) == "duplicate"


def test_server_realtime_concealment_then_repair(state):
    for s in range(1, 10):
        _send(state, s, now=float(s))
    assert state.conceal_overdue(now=9.5) == 0         # not overdue yet
    assert state.conceal_overdue(now=12.0) == 1        # 3 s late -> provisional forecast
    assert state.nodes["BUOY_07"].records[-1]["provisional"]
    assert _send(state, 12, now=13.0) == "reconstructed 2"
    recs = list(state.nodes["BUOY_07"].records)
    assert not any(r.get("provisional") for r in recs)
    assert [r["seq"] for r in recs][-3:] == [10, 11, 12]


def test_server_node_reboot_starts_fresh_stream(state):
    for s in range(1, 20):
        _send(state, s)
    assert _send(state, 1) == "ok"
    assert state.nodes["BUOY_07"].last_seq == 1


def test_predict_fuses_satellite_and_raises_alert(state):
    for s in range(1, 8):
        _send(state, s)
    assert state.predict()["alert"] is False
    sat = {"node": "SAT_GS_01", "seq": 1, "kind": "edge_feature", "sat_risk": 90.0, "risk_flag": True,
           "raw_bytes": 2_000_000, "sent_bytes": 1000}
    state.ingest(sat)
    pred = state.predict()
    assert pred["alert"] is True and pred["components"]["satellite"] == 90.0
    assert state.metrics()["bandwidth"]["reduction_pct"] == 99.95


def test_api_endpoints(state, monkeypatch):
    from fastapi.testclient import TestClient

    import central_server
    monkeypatch.setattr(central_server, "STATE", state)
    for s in range(1, 8):
        _send(state, s)
    client = TestClient(central_server.app)
    assert client.get("/health").json() == {"ok": True}
    assert "BUOY_07" in client.get("/predict").json()["nodes"]
    assert client.get("/telemetry/BUOY_07?limit=3").json()["records"][-1]["seq"] == 7
    assert "recovery" in client.get("/metrics").json()
    assert "series" in client.get("/snapshot").json()
    assert "<canvas" in client.get("/").text
    with client.websocket_connect("/ws") as ws:
        assert "series" in ws.receive_json()


# ------------------------------------------------------------------ hardware formats
def test_esp32_json_is_accepted_by_gateway():
    from edge_gateway import Gateway
    gw = Gateway(policy="rule", verbose=False)
    esp32 = (b'{"node":"BUOY_HW_01","seq":42,"time":"","t_sent":0,"wind":18.50,"temp":29.10,'
             b'"pressure":1006.30,"kind":"sensor","reconstructed":false}')
    assert gw.handle_packet(esp32)["traffic_class"] == TRAFFIC_NORMAL
    hk = b'{"node":"BUOY_HW_01","seq":9,"time":"","kind":"housekeeping","battery_v":0.00,"rssi":-61}'
    assert gw.handle_packet(hk)["traffic_class"] == TRAFFIC_NON_ESSENTIAL


def test_lora_serial_bridge_parsing():
    from hardware.serial_bridge import parse_line
    rec, hk = parse_line("B07,42,18.50,29.10,1006.30,-87,7.25\n")
    assert rec["node"] == "BUOY_LORA_07" and rec["seq"] == 42 and rec["pressure"] == 1006.3
    assert validate(rec) and hk["rssi"] == -87
    assert parse_line("# LoRa receiver ready") is None
    assert parse_line("garbage,line") is None
