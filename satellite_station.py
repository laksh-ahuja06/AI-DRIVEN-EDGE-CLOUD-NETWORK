"""
Satellite Ground Station (edge node)
-------------------------------------
Spec section 9.3 / Example 4: a ground station receives large
multi-spectral satellite frames. Instead of forwarding the raw frame over
the constrained backbone, it runs edge AI locally (edge_ai.extract_features)
and forwards only a compact feature record + risk flag.

The frames here are synthetic (4 bands: visible, infrared, water vapour,
near-IR; 512x512, 16-bit): a spiral cloud system that organises, grows
cold cloud tops and finally forms an eye as the cyclone intensifies.
Swap `SyntheticImager` for real INSAT-3D / Himawari tiles later.

Each forwarded record reports `raw_bytes` and `sent_bytes`, so the
central server can show the bandwidth reduction live.

Usage:
    python satellite_station.py --node SAT_GS_01 --interval 3 --cyclone-after 15
    python satellite_station.py --save-frames frames/   # also writes PNG previews
"""
import argparse
import os
import socket
import time
import zlib

import numpy as np

from common import GATEWAY_HOST, KIND_EDGE_FEATURE, SENSOR_TO_GATEWAY_PORT, encode
from edge_ai import BAND_IR, BAND_NIR, BAND_VIS, BAND_WV, IR_SCALE, extract_features


class SyntheticImager:
    def __init__(self, size=512, seed=0):
        self.size = size
        self.rng = np.random.default_rng(seed)
        ys, xs = np.mgrid[0:size, 0:size].astype(np.float32) / size
        self.ys, self.xs = ys, xs

    def _smooth_noise(self, scale):
        n = self.size // scale
        coarse = self.rng.random((n + 1, n + 1)).astype(np.float32)
        # Bilinear upsample of a coarse random grid -> smooth cloud texture.
        idx = np.linspace(0, n, self.size, dtype=np.float32)
        i0 = np.floor(idx).astype(int).clip(0, n - 1)
        f = idx - i0
        rows = coarse[i0] * (1 - f)[:, None] + coarse[i0 + 1] * f[:, None]
        return rows[:, i0] * (1 - f)[None, :] + rows[:, i0 + 1] * f[None, :]

    def frame(self, intensity, centre=(0.5, 0.5), rotation=0.0):
        """intensity 0 (fair weather) .. 1 (mature cyclone with eye)."""
        cx, cy = centre
        dx, dy = self.xs - cx, self.ys - cy
        r = np.hypot(dx, dy) + 1e-6
        theta = np.arctan2(dy, dx)

        # Background: scattered low/warm cumulus.
        background = 0.35 * self._smooth_noise(32) * self._smooth_noise(8)

        cloud = background
        if intensity > 0:
            radius = 0.08 + 0.17 * intensity
            arms = 0.5 + 0.5 * np.cos(2 * (theta - rotation) + 6.0 * np.log(r / radius + 1e-3))
            organisation = 0.3 + 0.7 * intensity
            spiral = np.exp(-((r / (radius * 1.6)) ** 2)) * (organisation * arms ** 2 + (1 - organisation) * 0.6)
            overcast = np.exp(-((r / (0.6 * radius)) ** 2)) * min(1.0, 0.3 + intensity)
            cloud = np.maximum(background, np.maximum(np.sqrt(intensity) * spiral, overcast))
            if intensity > 0.65:  # clear eye forms in mature storms
                eye_r = 0.008 + 0.006 * intensity
                cloud = cloud * (1 - np.exp(-((r / eye_r) ** 2)))

        cloud = np.clip(cloud + 0.03 * self.rng.standard_normal(cloud.shape).astype(np.float32), 0, 1)
        ir_k = 300.0 - 105.0 * cloud ** 0.6       # deep convection -> cold tops ~195 K
        vis = 0.06 + 0.85 * cloud
        wv_k = 255.0 - 30.0 * cloud
        nir = 0.04 + 0.7 * cloud

        img = np.empty((4, self.size, self.size), dtype=np.uint16)
        img[BAND_VIS] = np.clip(vis * 10000, 0, 65535)
        img[BAND_IR] = np.clip(ir_k * IR_SCALE, 0, 65535)
        img[BAND_WV] = np.clip(wv_k * IR_SCALE, 0, 65535)
        img[BAND_NIR] = np.clip(nir * 10000, 0, 65535)
        return img


def intensity_at(elapsed, cyclone_after, ramp_seconds):
    """Storm develops over `ramp_seconds`, holds, then decays (landfall)."""
    if not cyclone_after or elapsed < cyclone_after:
        return 0.0
    x = (elapsed - cyclone_after) / ramp_seconds
    if x < 1:
        return x
    if x < 1.6:
        return 1.0
    return max(0.0, 1.0 - (x - 1.6))


def save_png(image, path):
    from PIL import Image
    ir = image[BAND_IR].astype(np.float32) / IR_SCALE
    u8 = np.clip((300.0 - ir) / 110.0 * 255.0, 0, 255).astype(np.uint8)
    Image.fromarray(u8, mode="L").save(path)


def build_record(node_id, seq, image, feats):
    raw_bytes = image.nbytes
    record = {
        "node": node_id,
        "seq": seq,
        "time": time.strftime("%H:%M:%S"),
        "t_sent": round(time.time(), 3),
        "kind": KIND_EDGE_FEATURE,
        "raw_bytes": raw_bytes,
        **feats,
    }
    record["sent_bytes"] = 0
    record["sent_bytes"] = len(encode(record))
    return record


def run_station(node_id, interval, cyclone_after, ramp_seconds, size, gateway_host, gateway_port,
                save_frames=None, count=None, report_zlib=True):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    imager = SyntheticImager(size=size, seed=zlib.crc32(node_id.encode()) & 0xFFFF)
    if save_frames:
        os.makedirs(save_frames, exist_ok=True)
    print(f"[{node_id}] satellite ground station -> {gateway_host}:{gateway_port}")
    start = time.time()
    seq = 0
    while count is None or seq < count:
        seq += 1
        elapsed = time.time() - start
        intensity = intensity_at(elapsed, cyclone_after, ramp_seconds)
        # The storm drifts across the scene and rotates.
        centre = (0.35 + 0.3 * min(1.0, elapsed / (cyclone_after + 2 * ramp_seconds + 1e-6)), 0.5)
        image = imager.frame(intensity, centre=centre, rotation=0.4 * seq)

        t0 = time.perf_counter()
        feats = extract_features(image)
        infer_ms = (time.perf_counter() - t0) * 1000
        record = build_record(node_id, seq, image, feats)
        record["infer_ms"] = round(infer_ms, 1)
        if report_zlib:
            record["zlib_bytes"] = len(zlib.compress(image.tobytes(), 6))
            record["sent_bytes"] = len(encode(record))
        sock.sendto(encode(record), (gateway_host, gateway_port))

        reduction = 100 * (1 - record["sent_bytes"] / record["raw_bytes"])
        print(f"[{node_id}] frame {seq:04d} intensity={intensity:.2f} sat_risk={feats['sat_risk']:5.1f} "
              f"flag={feats['risk_flag']!s:5} raw={record['raw_bytes'] / 1e6:.2f} MB -> "
              f"{record['sent_bytes']} B ({reduction:.3f}% saved, {infer_ms:.0f} ms)")
        if save_frames:
            save_png(image, os.path.join(save_frames, f"{node_id}_{seq:04d}.png"))
        time.sleep(max(0.0, interval - (time.time() - start - elapsed)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Satellite ground station with edge AI")
    parser.add_argument("--node", default="SAT_GS_01")
    parser.add_argument("--interval", type=float, default=3.0, help="Seconds between frames")
    parser.add_argument("--cyclone-after", type=float, default=20.0, help="0 disables the cyclone")
    parser.add_argument("--ramp", type=float, default=40.0, help="Seconds for the storm to mature")
    parser.add_argument("--size", type=int, default=512, help="Frame size in pixels")
    parser.add_argument("--gateway-host", default=GATEWAY_HOST)
    parser.add_argument("--gateway-port", type=int, default=SENSOR_TO_GATEWAY_PORT)
    parser.add_argument("--save-frames", help="Directory to write IR PNG previews")
    parser.add_argument("--count", type=int)
    args = parser.parse_args()
    try:
        run_station(args.node, args.interval, args.cyclone_after, args.ramp, args.size,
                    args.gateway_host, args.gateway_port, args.save_frames, args.count)
    except KeyboardInterrupt:
        print(f"[{args.node}] stopped")
