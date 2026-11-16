# -*- coding: utf-8 -*-
"""
phantom.py — Deterministic dark-field microcirculation velocity phantom (v1.0)

Synthesises incident-dark-field-like image sequences of an RBC train flowing in a
single vessel over a fixed tissue plate, with controllable velocity, vessel width,
RBC contrast, photon noise and global drift. Fully deterministic (numpy default_rng,
seed 42); the canonical 144-condition sweep reproduces the archived reference table
of the companion manuscript bit-identically (same rng consumption order).

Two modes:
  canonical_sweep_frames()  — generator over the 144 published grid conditions,
                              shared rng stream, EXACT reproduction of the paper's table.
  make_condition(...)       — single condition, per-condition derived seed
                              (statistically equivalent, not bit-identical).
"""
import numpy as np
import cv2

SEED = 42
H, W, T = 200, 300, 125          # frames, pixels
GAP = 25.0                       # RBC train spacing (px)
BAND_Y0, BAND_Y1 = 99, 102       # vessel-centre sampling rows (y=100 vessel)

VS = [0.0, 0.2, 0.5, 1.0, 2.0, 3.0]      # px/frame
WIDTHS = [4, 8, 12]                       # px
CONTRASTS = [15, 40]
SIGMAS = [3, 6]
DRIFTS = [0.0, 0.5]

# Canonical sweep order (sigma -> drift -> contrast -> width -> v), as archived
GRID = [(sigma, drift, contrast, width, v)
        for sigma in SIGMAS for drift in DRIFTS for contrast in CONTRASTS
        for width in WIDTHS for v in VS]


def _build_tissue(rng):
    """Fixed tissue plate (consumes the first three rng draws; keep order stable)."""
    yy, xx = np.mgrid[0:H, 0:W]
    tissue = np.full((H, W), 150.0, np.float32)
    for (y0, sl, depth, wid) in [(20, 0.02, 80, 8), (60, -0.03, 95, 6), (100, 0.01, 110, 12),
                                 (140, 0.03, 90, 7), (175, -0.02, 75, 5)]:
        line = yy - (y0 + sl * (xx - W / 2))
        tissue -= depth * np.exp(-(line ** 2) / (2 * wid ** 2))
    tissue += cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.5) * 3
    tissue += rng.normal(0, 8.0, (H, W)).astype(np.float32)
    tissue = np.clip(tissue, 15, 220)
    ph = float(rng.uniform(0, 25.0))       # RBC-train phase, fixed across the whole grid
    return tissue, ph


def _render(v_true, width, contrast, drift, tissue, ph):
    """Noise-free frames for one condition (deterministic given tissue/phase)."""
    half = max(2, width // 2)
    ys = np.arange(100 - half, 100 + half + 1)
    ksig = max(1.0, width / 4.0)
    kdx = np.arange(-(half + 2), half + 3)
    kw = np.exp(-kdx ** 2 / (2 * ksig ** 2))
    frames = np.zeros((T, H, W), np.float32)
    for t in range(T):
        f = tissue.copy()
        for k in range(-1, int(W / GAP) + 2):
            xk = ph + k * GAP + v_true * t
            xi = int(round(xk)) % W
            cols = (xi + kdx) % W
            f[np.ix_(ys, cols)] += (-contrast) * kw[None, :] / kw.sum() * len(ys)
        M = np.float32([[1, 0, drift * t], [0, 1, 0.22 * drift * t]])
        frames[t] = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP,
                                   borderMode=cv2.BORDER_REFLECT_101)
    return frames


def canonical_sweep_frames():
    """Yield (condition, frames) over the 144 published conditions.

    A single rng stream (seed 42) is consumed exactly as in the archived sweep:
    tissue build first, then one noise draw per condition in canonical order.
    Bit-identical to the manuscript's reference table.
    """
    rng = np.random.default_rng(SEED)
    tissue, ph = _build_tissue(rng)
    for (sigma, drift, contrast, width, v) in GRID:
        frames = _render(v, width, contrast, drift, tissue, ph)
        frames = frames + rng.normal(0, sigma, frames.shape).astype(np.float32)
        cond = {"v_true_px_per_frame": v, "width_px": width, "rbc_contrast": contrast,
                "noise_sigma": sigma, "drift_px_per_frame": drift}
        yield cond, frames


def make_condition(v, width, contrast, sigma, drift, seed=None):
    """Single condition with a derived seed (default: deterministic from parameters).

    Statistically equivalent to the canonical grid cell but NOT bit-identical
    (the canonical table shares one noise stream across the sweep).
    """
    if seed is None:
        seed = (int(v * 1000) * 1000003 + width * 1009 + contrast * 101 + sigma * 7 + int(drift * 10)) % (2 ** 31)
    rng = np.random.default_rng(seed)
    tissue, ph = _build_tissue(rng)
    frames = _render(v, width, contrast, drift, tissue, ph)
    frames = frames + rng.normal(0, sigma, frames.shape).astype(np.float32)
    return {"v_true_px_per_frame": v, "width_px": width, "rbc_contrast": contrast,
            "noise_sigma": sigma, "drift_px_per_frame": drift}, frames
