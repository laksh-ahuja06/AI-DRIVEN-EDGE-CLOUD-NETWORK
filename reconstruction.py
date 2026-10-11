"""
Predictive packet-loss concealment (spec section 9.5).

Two situations need estimated values:

1. Gap repair (after the fact): packets seq=n+1..m-1 were lost, and both
   the record before the gap and the one after it are known.
     * "linear" - straight-line interpolation between the two (baseline).
     * "lstm"   - the LSTM forecasts forward from the recent history; the
                  forecast is then corrected so it lands exactly on the
                  record received after the gap (forecast + bridge).
2. Real-time concealment (before the next packet arrives): a node's packet
   is overdue. Interpolation is impossible because there is no "after"
   point yet, so the only options are holding the last value or
   forecasting. The LSTM forecast is published immediately and marked
   provisional; it is replaced once the real data or a gap repair arrives.

All estimated records are flagged `reconstructed: true` downstream.
"""
import os

import numpy as np

from lstm import LSTMRegressor

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
LSTM_MODEL_PATH = os.path.join(MODEL_DIR, "lstm_recon.npz")

WINDOW = 12  # readings of history the LSTM looks at
LEVEL_CENTER = np.array([30.0, 28.0, 1000.0])
LEVEL_SCALE = np.array([30.0, 2.0, 20.0])
DELTA_SCALE = np.array([5.0, 0.3, 2.0])
MIN_HISTORY = 4


def make_inputs(window):
    """window: (T, 3) array of wind/temp/pressure -> (T-1, 6) LSTM inputs."""
    w = np.asarray(window, dtype=np.float64)
    levels = (w[1:] - LEVEL_CENTER) / LEVEL_SCALE
    deltas = np.diff(w, axis=0) / DELTA_SCALE
    return np.concatenate([levels, deltas], axis=1)


def linear_fill(prev, nxt, n_missing):
    prev, nxt = np.asarray(prev, float), np.asarray(nxt, float)
    fracs = np.arange(1, n_missing + 1)[:, None] / (n_missing + 1)
    return prev + fracs * (nxt - prev)


class Reconstructor:
    def __init__(self, method="lstm", model_path=LSTM_MODEL_PATH):
        self.model = None
        self.method = "linear"
        if method == "lstm":
            if os.path.exists(model_path):
                self.model, _ = LSTMRegressor.load(model_path)
                self.method = "lstm"
            else:
                print(f"[reconstruction] {model_path} not found - falling back to linear "
                      f"interpolation (run `python train_models.py` to train the LSTM)")

    # -------------------------------------------------------------- forecast
    def forecast(self, history, steps):
        """Autoregressive forecast of the next `steps` readings. history: list of (w, t, p)."""
        hist = np.asarray(history[-(WINDOW + 1):], dtype=np.float64)
        if self.model is None or len(hist) < MIN_HISTORY:
            return np.repeat(hist[-1:], steps, axis=0)  # last-value hold
        out = []
        for _ in range(steps):
            x = make_inputs(hist)[None, :, :]
            delta = self.model.forward(x)[0] * DELTA_SCALE
            nxt = hist[-1] + delta
            out.append(nxt)
            hist = np.vstack([hist[1:] if len(hist) > WINDOW else hist, nxt])
        return np.array(out)

    # -------------------------------------------------------------- gap fill
    def fill_gap(self, history, nxt, n_missing):
        """
        history: readings up to and including the record before the gap.
        nxt: the reading received after the gap. Returns (n_missing, 3).
        """
        if n_missing <= 0:
            return np.zeros((0, 3))
        prev = history[-1]
        if self.model is None or len(history) < MIN_HISTORY:
            return linear_fill(prev, nxt, n_missing)
        fc = self.forecast(history, n_missing + 1)
        anchor_err = np.asarray(nxt, float) - fc[-1]
        fracs = np.arange(1, n_missing + 1)[:, None] / (n_missing + 1)
        return fc[:-1] + fracs * anchor_err
