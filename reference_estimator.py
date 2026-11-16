# -*- coding: utf-8 -*-
"""
reference_estimator.py — the manuscript's tile structure-tensor velocity estimator.

Pipeline (ident to the real-video layer): cumulative pairwise phase-correlation
registration -> temporal high-pass -> vessel-band space-time diagram -> tile-based
structure-tensor orientation -> median |velocity|.

An estimator module for run_benchmark.py must expose:
    estimate_velocity(frames) -> (v_est_px_per_frame, n_coherent_tiles)
"""
import numpy as np
import cv2

BAND_Y0, BAND_Y1 = 99, 102


def register_stack(frames, resp_gate=0.05):
    T, H, W = frames.shape
    win = cv2.createHanningWindow((W, H), cv2.CV_32F)
    reg = np.zeros_like(frames)
    cum = np.zeros(2)
    for t in range(T):
        if t > 0:
            (dx, dy), resp = cv2.phaseCorrelate(frames[t - 1], frames[t], win)
            if resp >= resp_gate:
                cum += np.array([dx, dy])
        M = np.float32([[1, 0, cum[0]], [0, 1, cum[1]]])
        reg[t] = cv2.warpAffine(frames[t], M, (W, H), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    return reg


def tile_velocities(xt, tile_t=32, tile_x=32, stride=16, min_coh=0.4):
    T, L = xt.shape
    out = []
    for t0 in range(0, T - tile_t + 1, stride):
        for x0 in range(0, L - tile_x + 1, stride):
            patch = xt[t0:t0 + tile_t, x0:x0 + tile_x]
            if patch.std() < 1e-6:
                continue
            ps = cv2.GaussianBlur(patch, (5, 1), 0)
            gt, gx = np.gradient(ps)
            Jxx = float((gx * gx).sum()); Jxt = float((gx * gt).sum()); Jtt = float((gt * gt).sum())
            tr = Jxx + Jtt
            if tr < 1e-9 or Jxx < 1e-9:
                continue
            disc = max(tr * tr / 4 - (Jxx * Jtt - Jxt * Jxt), 0.0)
            l1 = tr / 2 + np.sqrt(disc); l2 = tr / 2 - np.sqrt(disc)
            coh = 1 - l2 / l1 if l1 > 0 else 0.0
            if coh < min_coh:
                continue
            out.append(-Jxt / Jxx)
    return out


def estimate_velocity(frames):
    """Return (median |velocity| in px/frame, n coherent tiles); (None, n) if <3 tiles."""
    reg = register_stack(frames)
    hp = reg - reg.mean(axis=0, keepdims=True)
    xt = hp[:, BAND_Y0:BAND_Y1, 30:270].mean(axis=1)
    tiles = tile_velocities(xt)
    if len(tiles) < 3:
        return None, len(tiles)
    return abs(float(np.median(tiles))), len(tiles)
