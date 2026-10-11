"""
Edge AI components (spec sections 9.3 and 9.4).

1. Satellite imagery feature extraction
   `extract_features(image)` turns a multi-spectral frame (several MB raw)
   into a ~1 KB feature record: cold-cloud cover, coldest cloud top,
   storm centre, axisymmetry and eye contrast - the same cues a human
   forecaster uses in the Dvorak technique - plus a 0-100 risk score
   and a small IR thumbnail for the dashboard.

2. ML QoS classifier
   `QoSClassifier` is a logistic-regression model that looks at the recent
   *trend* of a node (pressure falling, wind rising) rather than only the
   current value. It is trained (train_models.py) to predict "this node
   will breach the cyclone thresholds within the next H readings", so it
   can raise priority *before* the rule-based classifier does.

Only numpy is required, so this runs on a Raspberry Pi.
"""
import base64
import os
from collections import deque

import numpy as np

from common import PRESSURE_CRITICAL_THRESHOLD, WIND_CRITICAL_THRESHOLD

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
QOS_MODEL_PATH = os.path.join(MODEL_DIR, "qos_classifier.npz")

# Band order of the synthetic imager (see satellite_station.py)
BAND_VIS, BAND_IR, BAND_WV, BAND_NIR = 0, 1, 2, 3
IR_SCALE = 100.0           # raw uint16 counts = brightness temperature (K) * IR_SCALE
COLD_CLOUD_K = 220.0       # cloud tops colder than this indicate deep convection
THUMB_SIZE = 24


# ---------------------------------------------------------------------------
# 1. Satellite imagery feature extraction
# ---------------------------------------------------------------------------
def _block_mean(a, size):
    h, w = a.shape
    fh, fw = h // size, w // size
    return a[: fh * size, : fw * size].reshape(size, fh, size, fw).mean(axis=(1, 3))


def extract_features(image):
    """
    image: uint16 array (bands, H, W). Returns a dict of compact features.
    """
    ir = image[BAND_IR].astype(np.float32) / IR_SCALE
    h, w = ir.shape
    cold = ir < COLD_CLOUD_K
    cold_frac = float(cold.mean())
    min_bt = float(ir.min())

    feats = {
        "cold_frac": round(cold_frac, 4),
        "min_bt": round(min_bt, 1),
        "centre": None,
        "symmetry": 0.0,
        "eye_contrast": 0.0,
    }

    if cold.sum() >= 0.002 * h * w:
        # Weight by "coldness" so the dense overcast dominates the centroid.
        weight = np.clip(COLD_CLOUD_K - ir, 0, None)
        ys, xs = np.mgrid[0:h, 0:w]
        total = weight.sum()
        cy, cx = float((weight * ys).sum() / total), float((weight * xs).sum() / total)
        feats["centre"] = [round(cx / w, 3), round(cy / h, 3)]

        r = np.hypot(ys - cy, xs - cx)
        theta = np.arctan2(ys - cy, xs - cx)
        radius = 0.18 * min(h, w)

        # Axisymmetry: cold-cloud cover in 8 angular sectors around the centre.
        ring = (r < radius) & (r > 0.03 * min(h, w))
        sector = ((theta + np.pi) / (2 * np.pi) * 8).astype(int) % 8
        cover = np.array([cold[ring & (sector == k)].mean() if (ring & (sector == k)).any() else 0.0
                          for k in range(8)])
        if cover.mean() > 0:
            feats["symmetry"] = round(float(np.clip(1.0 - cover.std() / cover.mean(), 0.0, 1.0)), 3)

        # Eye: a warm spot at the centre surrounded by a cold eyewall.
        eye = r < 0.015 * min(h, w)
        wall = (r > 0.03 * min(h, w)) & (r < 0.07 * min(h, w))
        if eye.any() and wall.any():
            feats["eye_contrast"] = round(float(ir[eye].mean() - ir[wall].mean()), 1)

    feats["sat_risk"] = satellite_risk(feats)
    feats["risk_flag"] = feats["sat_risk"] >= 60.0
    thumb = _block_mean(ir, THUMB_SIZE)
    thumb_u8 = np.clip((300.0 - thumb) / 110.0 * 255.0, 0, 255).astype(np.uint8)  # cold = bright
    feats["thumb"] = base64.b64encode(thumb_u8.tobytes()).decode("ascii")
    feats["thumb_size"] = THUMB_SIZE
    return feats


def satellite_risk(f):
    """
    Explainable 0-100 score (Dvorak-inspired):
      * organised deep convection covering the scene  -> up to 40
      * symmetric (axisymmetric) cloud pattern         -> up to 30
      * a warm eye inside a cold eyewall               -> up to 30
    """
    cover = min(1.0, f["cold_frac"] / 0.06)
    depth = min(1.0, max(0.0, (COLD_CLOUD_K - f["min_bt"]) / 25.0))
    eye = min(1.0, max(0.0, f["eye_contrast"] / 40.0))
    score = 40.0 * cover * depth + 30.0 * f["symmetry"] * cover + 30.0 * eye
    return round(float(min(100.0, score)), 1)


def decode_thumbnail(b64, size=THUMB_SIZE):
    return np.frombuffer(base64.b64decode(b64), dtype=np.uint8).reshape(size, size)


# ---------------------------------------------------------------------------
# 2. ML QoS classifier
# ---------------------------------------------------------------------------
HISTORY = 6  # readings of context used for trend features
FEATURE_NAMES = ["wind", "pressure", "wind_trend", "pressure_trend", "temp_trend", "wind_gap", "pressure_gap"]


def trend_features(window):
    """
    window: list of (wind, temp, pressure), oldest first, len >= 1.
    Returns the feature vector used by QoSClassifier.
    """
    w = np.asarray(window, dtype=np.float64)
    wind, temp, pres = w[-1]
    if len(w) >= 2:
        span = len(w) - 1
        wind_trend = (w[-1, 0] - w[0, 0]) / span
        temp_trend = (w[-1, 1] - w[0, 1]) / span
        pres_trend = (w[-1, 2] - w[0, 2]) / span
    else:
        wind_trend = temp_trend = pres_trend = 0.0
    return np.array([
        wind,
        pres,
        wind_trend,
        pres_trend,
        temp_trend,
        WIND_CRITICAL_THRESHOLD - wind,          # distance to the wind threshold
        pres - PRESSURE_CRITICAL_THRESHOLD,      # distance to the pressure threshold
    ])


class NodeHistory:
    """Keeps the last few readings per node so the gateway can compute trends."""

    def __init__(self, size=HISTORY):
        self.size = size
        self.windows = {}

    def update(self, record):
        dq = self.windows.setdefault(record["node"], deque(maxlen=self.size))
        dq.append((record["wind"], record["temp"], record["pressure"]))
        return list(dq)


class QoSClassifier:
    """Logistic regression with feature standardisation (numpy only)."""

    def __init__(self, weights=None, bias=0.0, mean=None, std=None, threshold=0.5):
        n = len(FEATURE_NAMES)
        self.w = np.zeros(n) if weights is None else np.asarray(weights, dtype=np.float64)
        self.b = float(bias)
        self.mean = np.zeros(n) if mean is None else np.asarray(mean, dtype=np.float64)
        self.std = np.ones(n) if std is None else np.asarray(std, dtype=np.float64)
        self.threshold = threshold

    def predict_proba(self, X):
        X = np.atleast_2d(X)
        z = ((X - self.mean) / self.std) @ self.w + self.b
        return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))

    def predict(self, X):
        return self.predict_proba(X) >= self.threshold

    def fit(self, X, y, epochs=400, lr=0.1, l2=1e-3, pos_weight=None):
        X = np.asarray(X, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        self.mean = X.mean(axis=0)
        self.std = X.std(axis=0) + 1e-9
        Xs = (X - self.mean) / self.std
        if pos_weight is None:
            pos_weight = (len(y) - y.sum()) / max(1.0, y.sum())
        sample_w = np.where(y > 0.5, pos_weight, 1.0)
        sample_w /= sample_w.mean()
        self.w = np.zeros(X.shape[1])
        self.b = 0.0
        for _ in range(epochs):  # full-batch gradient descent
            p = 1.0 / (1.0 + np.exp(-np.clip(Xs @ self.w + self.b, -30, 30)))
            g = sample_w * (p - y)
            self.w -= lr * (Xs.T @ g / len(y) + l2 * self.w)
            self.b -= lr * g.mean()
        return self

    def save(self, path=QOS_MODEL_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        np.savez(path, w=self.w, b=self.b, mean=self.mean, std=self.std, threshold=self.threshold)

    @classmethod
    def load(cls, path=QOS_MODEL_PATH):
        d = np.load(path)
        return cls(d["w"], float(d["b"]), d["mean"], d["std"], float(d["threshold"]))
