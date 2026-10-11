"""
Offline evaluation (spec section 12 "validation targets", section 13
"performance metrics", Appendix C "evaluation plan").

Runs four reproducible experiments on held-out simulated scenarios and
writes results/REPORT.md, results/results.json and PNG plots:

  1. Packet-loss recovery  - linear interpolation vs LSTM (gap repair) and
                             hold-last vs LSTM forecast (real-time concealment),
                             MAE/RMSE per variable at 5/10/20% bursty loss.
  2. QoS                   - FIFO (no QoS) vs priority scheduler on a constrained
                             backbone: critical delivery ratio and latency.
  3. QoS classifier        - rule vs ML vs hybrid: precision/recall for
                             "breach within 10 readings" and warning lead time.
  4. Edge AI bandwidth     - raw vs zlib vs edge features per satellite frame.

The QoS experiment uses the *same* QoSScheduler class as the live gateway,
driven by a simulated clock, so the numbers describe the real code.

Usage:
    python evaluate.py            # ~1 minute
    python evaluate.py --quick
"""
import argparse
import json
import os
import random
import time
import zlib

import numpy as np

from common import (TRAFFIC_CLASSES, TRAFFIC_CRITICAL, TRAFFIC_NON_ESSENTIAL, TRAFFIC_NORMAL, classify_traffic,
                    encode, make_housekeeping, make_telemetry)
from edge_ai import HISTORY, QOS_MODEL_PATH, QoSClassifier, extract_features, trend_features
from ocean_model import CycloneParams, GilbertElliottLink, OceanNode
from qos import QoSScheduler
from reconstruction import MIN_HISTORY, Reconstructor, linear_fill
from satellite_station import SyntheticImager, build_record
from train_models import QOS_HORIZON, breach, simulate_traces

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
VARS = ("wind", "temp", "pressure")


# ---------------------------------------------------------------------------
# 1. Packet-loss recovery
# ---------------------------------------------------------------------------
def eval_recovery(traces, loss_rates=(0.05, 0.10, 0.20), burst=0.6):
    lstm = Reconstructor("lstm")
    buckets = (("1", 1, 1), ("2-3", 2, 3), ("4+", 4, 10 ** 9))
    out = {}
    for loss in loss_rates:
        err = {"linear": [], "lstm": [], "hold": [], "forecast": []}
        by_gap = {b: {"linear": [], "lstm": []} for b, _, _ in buckets}
        gap_lengths = []
        for k, tr in enumerate(traces):
            link = GilbertElliottLink(loss, burstiness=burst, seed=1000 + k)
            lost = np.array([link.lost() for _ in range(len(tr))])
            lost[:MIN_HISTORY + 1] = False
            # Like the server, earlier gaps in the history are already filled
            # with the model's own estimates (never with the hidden truth).
            repaired = np.array(tr, dtype=float)
            t = 0
            while t < len(tr):
                if not lost[t]:
                    t += 1
                    continue
                start = t
                while t < len(tr) and lost[t]:
                    t += 1
                if t >= len(tr):
                    break  # gap still open at the end of the trace
                n = t - start
                gap_lengths.append(n)
                hist = list(repaired[:start])
                truth = tr[start:t]
                lin = linear_fill(tr[start - 1], tr[t], n)
                fill = lstm.fill_gap(hist, tr[t], n)
                repaired[start:t] = fill
                err["linear"].append(lin - truth)
                err["lstm"].append(fill - truth)
                err["hold"].append(np.repeat(np.asarray(hist[-1])[None], n, axis=0) - truth)
                err["forecast"].append(lstm.forecast(hist, n) - truth)
                for name, lo, hi in buckets:
                    if lo <= n <= hi:
                        by_gap[name]["linear"].append(lin - truth)
                        by_gap[name]["lstm"].append(fill - truth)
        res = {"gaps": len(gap_lengths), "mean_gap": round(float(np.mean(gap_lengths)), 2) if gap_lengths else 0,
               "lost_readings": int(sum(gap_lengths))}
        for method, errs in err.items():
            e = np.concatenate(errs) if errs else np.zeros((1, 3))
            res[method] = {v: {"mae": round(float(np.abs(e[:, i]).mean()), 3),
                               "rmse": round(float(np.sqrt((e[:, i] ** 2).mean())), 3)} for i, v in enumerate(VARS)}
        res["by_gap"] = {}
        for name, d in by_gap.items():
            if d["linear"]:
                res["by_gap"][name] = {"readings": int(sum(len(x) for x in d["linear"]))}
                for method in ("linear", "lstm"):
                    e = np.concatenate(d[method])
                    res["by_gap"][name][method] = {v: round(float(np.abs(e[:, i]).mean()), 3)
                                                   for i, v in enumerate(VARS)}
        out[f"{int(loss * 100)}%"] = res
    return out, lstm.method


# ---------------------------------------------------------------------------
# 2. QoS scheduler: FIFO vs priority on a constrained backbone
# ---------------------------------------------------------------------------
def generate_traffic(duration=300, n_sensors=4, seed=5, clf=None):
    """Arrivals at the gateway: (time, class, size_bytes, node)."""
    rng = random.Random(seed)
    arrivals = []
    for s in range(n_sensors):
        node_id = f"BUOY_{s:02d}"
        ocean = OceanNode(CycloneParams(onset_step=40 + 25 * s, speed_km_per_step=8, closest_km=20 + 20 * s),
                          seed=seed * 10 + s)
        window = []
        phase = rng.random()
        for t in range(duration):
            wind, temp, pres = ocean.step()
            rec = make_telemetry(node_id, t + 1, wind, temp, pres)
            rec.update({"traffic_class": "NORMAL", "qos_policy": "hybrid", "ml_prob": 0.123, "t_gw": 0.0})
            window = (window + [(wind, temp, pres)])[-HISTORY:]
            cls = classify_traffic(rec)
            if clf is not None and clf.predict(trend_features(window))[0]:
                cls = TRAFFIC_CRITICAL
            arrivals.append((t + phase, cls, len(encode(rec)) + 28, node_id))
            if (t + 1) % 5 == 0:
                hk = make_housekeeping(node_id, t // 5, 3.7, -80)
                arrivals.append((t + phase + 0.01, TRAFFIC_NON_ESSENTIAL, len(encode(hk)) + 28, node_id))
    for t in range(0, duration, 3):  # satellite feature records
        arrivals.append((t + 0.5, TRAFFIC_CRITICAL if 120 < t < 220 else TRAFFIC_NORMAL, 1130, "SAT_GS_01"))
    arrivals.sort()
    return arrivals


def simulate_qos(arrivals, policy, rate_bps, alert_hold=10.0):
    sched = QoSScheduler(rate_bps=rate_bps, policy=policy, now=0.0)
    delays = {c: [] for c in TRAFFIC_CLASSES}
    offered = {c: 0 for c in TRAFFIC_CLASSES}
    now = 0.0
    last_crit = -1e9

    def drain(until):
        nonlocal now
        while True:
            wait = sched.next_ready_in(now)
            if wait is None or now + wait > until:
                return
            now += wait + 1e-9
            item = sched.dequeue(now)
            if item is not None:
                (t_arr, cls), _, _ = item
                delays[cls].append(now - t_arr)

    for t_arr, cls, size, _node in arrivals:
        drain(t_arr)
        now = max(now, t_arr)
        offered[cls] += 1
        if cls == TRAFFIC_CRITICAL:
            last_crit = t_arr
        sched.set_alert(t_arr - last_crit < alert_hold)
        sched.enqueue((t_arr, cls), cls, size, now)
    drain(now + 600)

    res = {}
    for c in TRAFFIC_CLASSES:
        d = sorted(delays[c])
        res[c] = {"offered": offered[c], "delivered": len(d),
                  "delivery_ratio": round(len(d) / offered[c], 4) if offered[c] else None,
                  "avg_ms": round(1000 * float(np.mean(d)), 1) if d else None,
                  "p95_ms": round(1000 * d[int(0.95 * (len(d) - 1))], 1) if d else None}
    return res


def eval_qos(rates=(1000, 1200, 1400, 2000), quick=False):
    clf = QoSClassifier.load(QOS_MODEL_PATH) if os.path.exists(QOS_MODEL_PATH) else None
    arrivals = generate_traffic(duration=200 if quick else 300, clf=clf)
    duration = arrivals[-1][0]
    offered_bps = sum(a[2] for a in arrivals) / duration
    out = {"offered_load_bps": round(offered_bps, 1), "runs": {}}
    for rate in rates:
        out["runs"][str(rate)] = {p: simulate_qos(arrivals, p, rate) for p in ("fifo", "priority")}
    return out


# ---------------------------------------------------------------------------
# 3. QoS classifier: rule vs ML vs hybrid
# ---------------------------------------------------------------------------
def eval_classifier(traces):
    if not os.path.exists(QOS_MODEL_PATH):
        return None
    clf = QoSClassifier.load(QOS_MODEL_PATH)
    stats = {m: {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "leads": [], "calm_false_alarms": 0}
             for m in ("rule", "ml", "hybrid")}
    calm_traces = 0
    for tr in traces:
        flags = np.array([breach(r) for r in tr])
        first_breach = int(np.argmax(flags)) if flags.any() else None
        if first_breach is None:
            calm_traces += 1
        first_flag = {m: None for m in stats}
        for t in range(len(tr) - QOS_HORIZON):
            label = bool(flags[t:t + QOS_HORIZON + 1].any())
            rule = bool(flags[t])
            ml = bool(clf.predict(trend_features(tr[max(0, t - HISTORY + 1):t + 1]))[0])
            for m, pred in (("rule", rule), ("ml", ml), ("hybrid", rule or ml)):
                s = stats[m]
                s["tp" if pred and label else "fp" if pred else "fn" if label else "tn"] += 1
                if pred and first_flag[m] is None:
                    first_flag[m] = t
        for m in stats:
            if first_breach is not None and first_flag[m] is not None:
                stats[m]["leads"].append(first_breach - first_flag[m])
            if first_breach is None and first_flag[m] is not None:
                stats[m]["calm_false_alarms"] += 1
    out = {"horizon": QOS_HORIZON, "calm_traces": calm_traces}
    for m, s in stats.items():
        p = s["tp"] / max(1, s["tp"] + s["fp"])
        r = s["tp"] / max(1, s["tp"] + s["fn"])
        out[m] = {"precision": round(p, 3), "recall": round(r, 3), "f1": round(2 * p * r / max(1e-9, p + r), 3),
                  "mean_lead_readings": round(float(np.mean(s["leads"])), 2) if s["leads"] else None,
                  "calm_traces_with_false_alarm": s["calm_false_alarms"]}
    return out


# ---------------------------------------------------------------------------
# 4. Edge AI bandwidth
# ---------------------------------------------------------------------------
def eval_bandwidth(sizes=(256, 512, 1024)):
    out = []
    for size in sizes:
        imager = SyntheticImager(size=size, seed=1)
        for intensity in (0.0, 0.5, 1.0):
            img = imager.frame(intensity, (0.45, 0.5), rotation=0.7)
            t0 = time.perf_counter()
            feats = extract_features(img)
            ms = (time.perf_counter() - t0) * 1000
            rec = build_record("SAT", 1, img, feats)
            z = len(zlib.compress(img.tobytes(), 6))
            out.append({"size": size, "intensity": intensity, "raw_bytes": img.nbytes, "zlib_bytes": z,
                        "feature_bytes": rec["sent_bytes"], "sat_risk": feats["sat_risk"],
                        "reduction_pct": round(100 * (1 - rec["sent_bytes"] / img.nbytes), 3),
                        "reduction_vs_zlib_pct": round(100 * (1 - rec["sent_bytes"] / z), 3),
                        "inference_ms": round(ms, 1)})
    return out


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def plots(results):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping plots")
        return []
    files = []
    rec = results["recovery"]
    losses = list(rec.keys())
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    for ax, var in zip(axes, ("wind", "pressure")):
        x = np.arange(len(losses))
        for j, (m, label) in enumerate((("linear", "Linear (gap)"), ("lstm", "LSTM (gap)"),
                                        ("hold", "Hold-last (real-time)"), ("forecast", "LSTM forecast (real-time)"))):
            ax.bar(x + (j - 1.5) * 0.2, [rec[l][m][var]["mae"] for l in losses], 0.2, label=label)
        ax.set_xticks(x, losses)
        ax.set_xlabel("packet loss rate (bursty)")
        ax.set_ylabel(f"{var} MAE ({'km/h' if var == 'wind' else 'hPa'})")
        ax.set_title(f"Reconstruction error - {var}")
    axes[0].legend(fontsize=7)
    fig.tight_layout()
    path = os.path.join(RESULTS, "recovery_mae.png")
    fig.savefig(path, dpi=130)
    files.append(path)

    qos = results["qos"]["runs"]
    rates = list(qos.keys())
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    x = np.arange(len(rates))
    for j, p in enumerate(("fifo", "priority")):
        axes[0].bar(x + (j - 0.5) * 0.35, [qos[r][p]["CRITICAL"]["p95_ms"] or 0 for r in rates], 0.35, label=p)
        axes[1].bar(x + (j - 0.5) * 0.35, [100 * (qos[r][p]["CRITICAL"]["delivery_ratio"] or 0) for r in rates],
                    0.35, label=p)
    axes[0].set_ylabel("critical p95 latency (ms)")
    axes[0].set_yscale("log")
    axes[1].set_ylabel("critical delivery ratio (%)")
    for ax in axes:
        ax.set_xticks(x, [f"{r} B/s" for r in rates])
        ax.set_xlabel("backbone capacity")
        ax.legend()
    fig.suptitle(f"QoS on a constrained backbone (offered load {results['qos']['offered_load_bps']} B/s)")
    fig.tight_layout()
    path = os.path.join(RESULTS, "qos.png")
    fig.savefig(path, dpi=130)
    files.append(path)
    plt.close("all")
    return files


def write_report(results, recon_method):
    L = ["# Evaluation report", "",
         "Generated by `python evaluate.py` on held-out simulated scenarios (ocean_model.py). "
         "These numbers measure the *mechanisms* on synthetic data; repeat with real buoy data before "
         "claiming field performance.", ""]

    L += ["## 1. Packet-loss recovery (MAE, lower is better)", "",
          f"Gilbert-Elliott bursty loss (burstiness 0.6). Reconstruction model: **{recon_method}**.", "",
          "| Loss | Gaps (mean length) | Variable | Linear (gap repair) | LSTM (gap repair) | "
          "Hold-last (real-time) | LSTM forecast (real-time) |",
          "|---|---|---|---|---|---|---|"]
    for loss, r in results["recovery"].items():
        for v in VARS:
            L.append(f"| {loss} | {r['gaps']} ({r['mean_gap']}) | {v} | {r['linear'][v]['mae']} | "
                     f"{r['lstm'][v]['mae']} | {r['hold'][v]['mae']} | {r['forecast'][v]['mae']} |")
    L += ["", "Gap repair uses the readings on both sides of the gap; real-time concealment only has the past "
          "(the next packet has not arrived yet), so linear interpolation is impossible there.", "",
          "Gap repair MAE by gap length (20% loss run):", "",
          "| Gap length | Lost readings | Wind linear | Wind LSTM | Pressure linear | Pressure LSTM |",
          "|---|---|---|---|---|---|"]
    worst = list(results["recovery"].values())[-1]
    for name, g in worst["by_gap"].items():
        L.append(f"| {name} | {g['readings']} | {g['linear']['wind']} | {g['lstm']['wind']} | "
                 f"{g['linear']['pressure']} | {g['lstm']['pressure']} |")
    L.append("")

    q = results["qos"]
    L += ["## 2. QoS on a constrained backbone", "",
          f"4 buoys + satellite station + housekeeping, offered load **{q['offered_load_bps']} B/s**. "
          "Same `QoSScheduler` code as the live gateway, simulated clock.", "",
          "| Backbone | Scheduler | Critical delivered | Critical avg / p95 ms | Normal delivered | "
          "Normal p95 ms | Non-essential delivered |", "|---|---|---|---|---|---|---|"]
    for rate, runs in q["runs"].items():
        for p, r in runs.items():
            c, n, ne = r[TRAFFIC_CRITICAL], r[TRAFFIC_NORMAL], r[TRAFFIC_NON_ESSENTIAL]
            pct = lambda x: f"{100 * x:.1f}%" if x is not None else "-"
            L.append(f"| {rate} B/s | {p} | {pct(c['delivery_ratio'])} | {c['avg_ms']} / {c['p95_ms']} | "
                     f"{pct(n['delivery_ratio'])} | {n['p95_ms']} | {pct(ne['delivery_ratio'])} |")
    L.append("")

    c = results["classifier"]
    if c:
        L += ["## 3. QoS classifier", "",
              f"Label: thresholds breached now or within the next {c['horizon']} readings.", "",
              "| Policy | Precision | Recall | F1 | Mean warning lead (readings before first breach) | "
              f"Calm traces with a false alarm (of {c['calm_traces']}) |", "|---|---|---|---|---|---|"]
        for m in ("rule", "ml", "hybrid"):
            r = c[m]
            L.append(f"| {m} | {r['precision']} | {r['recall']} | {r['f1']} | {r['mean_lead_readings']} | "
                     f"{r['calm_traces_with_false_alarm']} |")
        L.append("")

    L += ["## 4. Edge AI bandwidth (satellite frames, 4 bands, 16-bit)", "",
          "| Frame | Storm intensity | Raw | zlib | Sent (features) | Saved vs raw | Saved vs zlib | "
          "Edge risk | Inference ms |", "|---|---|---|---|---|---|---|---|---|"]
    for b in results["bandwidth"]:
        L.append(f"| {b['size']}x{b['size']} | {b['intensity']} | {b['raw_bytes'] / 1e6:.2f} MB | "
                 f"{b['zlib_bytes'] / 1e6:.2f} MB | {b['feature_bytes']} B | {b['reduction_pct']}% | "
                 f"{b['reduction_vs_zlib_pct']}% | {b['sat_risk']} | {b['inference_ms']} |")
    L.append("")
    if results.get("plots"):
        L += ["## Plots", ""] + [f"![{os.path.basename(p)}]({os.path.basename(p)})" for p in results["plots"]]
    with open(os.path.join(RESULTS, "REPORT.md"), "w") as f:
        f.write("\n".join(L) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    os.makedirs(RESULTS, exist_ok=True)
    traces = simulate_traces(20 if args.quick else 60, 200, seed=99)  # unseen during training

    print("1/4 packet-loss recovery...")
    recovery, method = eval_recovery(traces)
    print("2/4 QoS scheduler...")
    qos = eval_qos(quick=args.quick)
    print("3/4 QoS classifier...")
    classifier = eval_classifier(traces)
    print("4/4 edge AI bandwidth...")
    bandwidth = eval_bandwidth((256, 512) if args.quick else (256, 512, 1024))

    results = {"recovery": recovery, "qos": qos, "classifier": classifier, "bandwidth": bandwidth}
    results["plots"] = plots(results)
    with open(os.path.join(RESULTS, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
    write_report(results, method)
    print(f"wrote {os.path.join(RESULTS, 'REPORT.md')}")


if __name__ == "__main__":
    main()
