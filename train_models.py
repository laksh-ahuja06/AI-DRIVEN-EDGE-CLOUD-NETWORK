"""
Train the two learned components on simulated cyclone scenarios:

  models/lstm_recon.npz       LSTM used for packet-loss reconstruction
  models/qos_classifier.npz   logistic-regression QoS classifier

Training data comes from ocean_model.py (randomised cyclone tracks,
intensities and calm-weather traces). When you get real buoy data
(e.g. INCOIS / NOAA NDBC CSVs), load it into the same (T, 3) arrays of
wind/temp/pressure and reuse `lstm_dataset` / `qos_dataset` unchanged.

Usage:
    python train_models.py            # ~1-2 minutes on a laptop CPU
    python train_models.py --quick    # smaller run for testing
"""
import argparse
import os
import random
import time

import numpy as np

from common import PRESSURE_CRITICAL_THRESHOLD, WIND_CRITICAL_THRESHOLD
from edge_ai import HISTORY, QOS_MODEL_PATH, QoSClassifier, trend_features
from lstm import LSTMRegressor
from ocean_model import OceanNode, random_cyclone_params
from reconstruction import DELTA_SCALE, LSTM_MODEL_PATH, WINDOW, make_inputs

QOS_HORIZON = 10  # "will breach thresholds within the next N readings"


def simulate_traces(n_traces, length, seed):
    rng = random.Random(seed)
    traces = []
    for k in range(n_traces):
        node = OceanNode(random_cyclone_params(rng, length), seed=seed * 100003 + k)
        traces.append(np.array(node.trace(length)))
    return traces


def lstm_dataset(traces, stride=2):
    X, Y = [], []
    for tr in traces:
        for start in range(0, len(tr) - WINDOW - 1, stride):
            window = tr[start:start + WINDOW + 1]
            X.append(make_inputs(window))
            Y.append((tr[start + WINDOW + 1] - tr[start + WINDOW]) / DELTA_SCALE)
    return np.array(X), np.array(Y)


def breach(reading):
    return reading[0] >= WIND_CRITICAL_THRESHOLD or reading[2] <= PRESSURE_CRITICAL_THRESHOLD


def qos_dataset(traces, horizon=QOS_HORIZON):
    X, y = [], []
    for tr in traces:
        flags = np.array([breach(r) for r in tr])
        for t in range(len(tr) - horizon):
            window = tr[max(0, t - HISTORY + 1):t + 1]
            X.append(trend_features(window))
            y.append(float(flags[t:t + horizon + 1].any()))
    return np.array(X), np.array(y)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--hidden", type=int, default=32)
    args = parser.parse_args()

    n_train, n_val = (60, 15) if args.quick else (240, 40)
    epochs = args.epochs or (4 if args.quick else 20)
    os.makedirs(os.path.dirname(LSTM_MODEL_PATH), exist_ok=True)

    print(f"Simulating {n_train + n_val} cyclone scenarios...")
    train = simulate_traces(n_train, 200, seed=1)
    val = simulate_traces(n_val, 200, seed=2)

    # ---- LSTM ------------------------------------------------------------
    X, Y = lstm_dataset(train)
    Xv, Yv = lstm_dataset(val, stride=5)
    print(f"LSTM: {len(X)} training windows, {len(Xv)} validation windows, hidden={args.hidden}")
    model = LSTMRegressor(n_in=X.shape[2], n_hidden=args.hidden, n_out=Y.shape[1], seed=0)
    t0 = time.time()
    model.fit(X, Y, epochs=epochs, batch_size=64, lr=3e-3, X_val=Xv, Y_val=Yv)
    persistence = float((Yv ** 2).mean())  # "no change" forecast for reference
    print(f"LSTM trained in {time.time() - t0:.0f}s; val mse={((model.forward(Xv) - Yv) ** 2).mean():.4f} "
          f"vs {persistence:.4f} for a no-change forecast")
    model.save(LSTM_MODEL_PATH, window=WINDOW)
    print(f"saved {LSTM_MODEL_PATH}")

    # ---- QoS classifier ----------------------------------------------------
    Xq, yq = qos_dataset(train)
    Xqv, yqv = qos_dataset(val)
    clf = QoSClassifier().fit(Xq, yq)
    pred = clf.predict(Xqv)
    tp = float((pred & (yqv > 0.5)).sum())
    precision = tp / max(1.0, pred.sum())
    recall = tp / max(1.0, yqv.sum())
    print(f"QoS classifier: {len(Xq)} samples ({yq.mean():.1%} positive); "
          f"val precision={precision:.3f} recall={recall:.3f}")
    clf.save(QOS_MODEL_PATH)
    print(f"saved {QOS_MODEL_PATH}")


if __name__ == "__main__":
    main()
