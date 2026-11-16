# -*- coding: utf-8 -*-
"""
run_benchmark.py — score any dark-field velocity estimator on the 144-condition
deterministic phantom grid.

Usage:
  python run_benchmark.py                     # reference estimator -> benchmark_results.csv
  python run_benchmark.py --estimator my_mod  # your module (needs estimate_velocity(frames))
  python run_benchmark.py --check             # re-run reference & verify against
                                              # reference_results.csv (exact, 3 dp)

Pass criterion (pre-specified): v>0: |v_rec - v_true| <= max(0.10, 0.25*v_true);
                                v=0: v_rec < 0.10.
"""
import argparse
import importlib
import csv
import io
import os
import time

import phantom
import reference_estimator as ref

HERE = os.path.dirname(os.path.abspath(__file__))


def passes(v_true, v_rec):
    if v_rec is None:
        return False
    return (v_rec < 0.10) if v_true == 0 else (abs(v_rec - v_true) <= max(0.10, 0.25 * v_true))


def sweep(estimate):
    rows = []
    t0 = time.time()
    for i, (cond, frames) in enumerate(phantom.canonical_sweep_frames(), start=1):
        v_rec, ntile = estimate(frames)
        v = cond["v_true_px_per_frame"]
        rows.append({**cond,
                     "v_recovered_px_per_frame": round(v_rec, 3) if v_rec is not None else None,
                     "v_ratio_rec_true": round(v_rec / v, 3) if (v_rec is not None and v > 0) else None,
                     "n_cohesive_tiles": ntile,
                     "pass_envelope": passes(v, v_rec)})
        if i % 24 == 0:
            print("  %3d/144 conditions (%.0fs)" % (i, time.time() - t0))
    return rows


def write_csv(rows, path):
    with io.open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def check(rows, ref_path):
    ref_rows = list(csv.DictReader(io.open(ref_path, encoding="utf-8-sig")))
    assert len(ref_rows) == len(rows) == 144, "row count %d vs %d" % (len(ref_rows), len(rows))
    bad = 0
    for a, b in zip(ref_rows, rows):
        for k in ("v_true_px_per_frame", "width_px", "rbc_contrast", "noise_sigma", "drift_px_per_frame"):
            if float(a[k]) != float(b[k]):
                bad += 1; print("condition mismatch", k, a, b); break
        va = a["v_recovered_px_per_frame"]
        vb = b["v_recovered_px_per_frame"]
        if (va is None) != (vb is None) or (va is not None and abs(float(va) - float(vb)) > 5e-4):
            bad += 1
            print("value mismatch: ref=%s new=%s (%s)" % (va, vb, a))
        if str(a["pass_envelope"]).lower() != str(b["pass_envelope"]).lower():
            bad += 1
            print("pass mismatch", a, b)
    print("CHECK: %d/144 conditions verified%s" % (144 - bad, " — ALL MATCH" if bad == 0 else " — %d MISMATCHES" % bad))
    return bad == 0


def summary(rows):
    n = len(rows)
    pr = sum(r["pass_envelope"] for r in rows) / n
    v0 = [r for r in rows if r["v_true_px_per_frame"] == 0]
    slow = [r for r in rows if 0 < r["v_true_px_per_frame"] <= 0.2]
    vmax = max((r["v_recovered_px_per_frame"] or 0) for r in v0)
    print("overall pass %.1f%% | zero-flow: %d/%d pass, max v_rec=%.3f px/f | slow-flow (v<=0.2): %d/%d pass"
          % (100 * pr, sum(r["pass_envelope"] for r in v0), len(v0), vmax,
             sum(r["pass_envelope"] for r in slow), len(slow)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimator", default=None, help="module with estimate_velocity(frames)")
    ap.add_argument("--check", action="store_true", help="verify reference reproduction")
    ap.add_argument("--out", default=None, help="output csv path")
    args = ap.parse_args()

    if args.estimator:
        mod = importlib.import_module(args.estimator)
        estimate = mod.estimate_velocity
    else:
        estimate = ref.estimate_velocity

    rows = sweep(estimate)
    out = args.out or os.path.join(HERE, "benchmark_results_%s.csv" % (args.estimator or "reference"))
    write_csv(rows, out)
    print("wrote", out)
    summary(rows)
    if args.check:
        ok = check(rows, os.path.join(HERE, "reference_results.csv"))
        raise SystemExit(0 if ok else 1)
