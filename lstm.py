"""
A small LSTM implemented in plain numpy (forward pass, backpropagation
through time and the Adam optimiser).

Why not PyTorch/TensorFlow? Those are 500 MB+ installs; this model has a
few thousand parameters, trains in about a minute on a laptop CPU and
runs inference on a Raspberry Pi with only numpy. The maths is the
standard LSTM cell:

    i = sigmoid(W_i [x, h] + b_i)      input gate
    f = sigmoid(W_f [x, h] + b_f)      forget gate
    o = sigmoid(W_o [x, h] + b_o)      output gate
    g = tanh   (W_g [x, h] + b_g)      candidate cell
    c' = f * c + i * g
    h' = o * tanh(c')
    y  = W_y h' + b_y                  linear read-out at the last step
"""
import numpy as np


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


class LSTMRegressor:
    def __init__(self, n_in, n_hidden, n_out, seed=0):
        rng = np.random.default_rng(seed)
        self.n_in, self.n_hidden, self.n_out = n_in, n_hidden, n_out
        scale = 1.0 / np.sqrt(n_in + n_hidden)
        self.params = {
            "W": rng.normal(0, scale, (n_in + n_hidden, 4 * n_hidden)),
            "b": np.zeros(4 * n_hidden),
            "Wy": rng.normal(0, 1.0 / np.sqrt(n_hidden), (n_hidden, n_out)),
            "by": np.zeros(n_out),
        }
        self.params["b"][n_hidden:2 * n_hidden] = 1.0  # forget-gate bias = 1 (standard trick)
        self._adam = None

    # ---------------------------------------------------------------- forward
    def forward(self, X, keep_cache=False):
        """X: (batch, time, n_in) -> (batch, n_out) prediction from the last step."""
        W, b = self.params["W"], self.params["b"]
        B, T, _ = X.shape
        H = self.n_hidden
        h = np.zeros((B, H))
        c = np.zeros((B, H))
        cache = []
        for t in range(T):
            z = np.concatenate([X[:, t, :], h], axis=1)
            a = z @ W + b
            i = _sigmoid(a[:, :H])
            f = _sigmoid(a[:, H:2 * H])
            o = _sigmoid(a[:, 2 * H:3 * H])
            g = np.tanh(a[:, 3 * H:])
            c_prev = c
            c = f * c_prev + i * g
            tc = np.tanh(c)
            h = o * tc
            if keep_cache:
                cache.append((z, i, f, o, g, c_prev, tc))
        y = h @ self.params["Wy"] + self.params["by"]
        if keep_cache:
            return y, (cache, h)
        return y

    # --------------------------------------------------------------- backward
    def loss_and_grads(self, X, Y):
        """Mean-squared error and gradients via backpropagation through time."""
        y, (cache, h_last) = self.forward(X, keep_cache=True)
        B = X.shape[0]
        H = self.n_hidden
        diff = y - Y
        loss = float((diff ** 2).mean())
        dy = 2.0 * diff / diff.size

        grads = {k: np.zeros_like(v) for k, v in self.params.items()}
        grads["Wy"] = h_last.T @ dy
        grads["by"] = dy.sum(axis=0)
        dh = dy @ self.params["Wy"].T
        dc = np.zeros((B, H))
        W = self.params["W"]
        for z, i, f, o, g, c_prev, tc in reversed(cache):
            do = dh * tc
            dc = dc + dh * o * (1 - tc ** 2)
            di = dc * g
            df = dc * c_prev
            dg = dc * i
            da = np.concatenate([
                di * i * (1 - i),
                df * f * (1 - f),
                do * o * (1 - o),
                dg * (1 - g ** 2),
            ], axis=1)
            grads["W"] += z.T @ da
            grads["b"] += da.sum(axis=0)
            dz = da @ W.T
            dh = dz[:, self.n_in:]
            dc = dc * f
        return loss, grads

    # ------------------------------------------------------------------ train
    def adam_step(self, grads, lr=3e-3, beta1=0.9, beta2=0.999, eps=1e-8, clip=5.0):
        if self._adam is None:
            self._adam = {"t": 0, "m": {k: np.zeros_like(v) for k, v in self.params.items()},
                          "v": {k: np.zeros_like(v) for k, v in self.params.items()}}
        norm = np.sqrt(sum(float((g ** 2).sum()) for g in grads.values()))
        if norm > clip:
            grads = {k: g * clip / norm for k, g in grads.items()}
        st = self._adam
        st["t"] += 1
        for k in self.params:
            st["m"][k] = beta1 * st["m"][k] + (1 - beta1) * grads[k]
            st["v"][k] = beta2 * st["v"][k] + (1 - beta2) * grads[k] ** 2
            m_hat = st["m"][k] / (1 - beta1 ** st["t"])
            v_hat = st["v"][k] / (1 - beta2 ** st["t"])
            self.params[k] -= lr * m_hat / (np.sqrt(v_hat) + eps)

    def fit(self, X, Y, epochs=20, batch_size=64, lr=3e-3, X_val=None, Y_val=None, seed=0, verbose=True):
        rng = np.random.default_rng(seed)
        history = []
        n = len(X)
        for epoch in range(epochs):
            order = rng.permutation(n)
            losses = []
            for start in range(0, n, batch_size):
                idx = order[start:start + batch_size]
                loss, grads = self.loss_and_grads(X[idx], Y[idx])
                self.adam_step(grads, lr=lr)
                losses.append(loss)
            train_loss = float(np.mean(losses))
            val_loss = float(((self.forward(X_val) - Y_val) ** 2).mean()) if X_val is not None else None
            history.append((train_loss, val_loss))
            if verbose:
                msg = f"  epoch {epoch + 1:3d}/{epochs}  train mse={train_loss:.5f}"
                if val_loss is not None:
                    msg += f"  val mse={val_loss:.5f}"
                print(msg)
        return history

    # -------------------------------------------------------------- save/load
    def save(self, path, **extra):
        np.savez(path, n_in=self.n_in, n_hidden=self.n_hidden, n_out=self.n_out, **self.params, **extra)

    @classmethod
    def load(cls, path):
        d = np.load(path)
        model = cls(int(d["n_in"]), int(d["n_hidden"]), int(d["n_out"]))
        for k in model.params:
            model.params[k] = d[k]
        extra = {k: d[k] for k in d.files if k not in model.params and k not in ("n_in", "n_hidden", "n_out")}
        return model, extra
