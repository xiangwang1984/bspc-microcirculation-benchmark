# Reference results — factor-wise pass rates (deterministic, seed 42)

Source: `reference_results.csv` (byte-copy of the manuscript archive
`RESULTS_TABLES/demo/velocity_phantom_envelope.csv`, 2026-09); regenerate and
verify with `python run_benchmark.py --check`.

## Headline numbers

| Metric | Value |
|---|---|
| Conditions | 144 |
| Overall pass rate | 38.9% |
| Zero-flow (v=0) pass | 24/24 (both drift levels) |
| Zero-flow max v_rec | 0.06 px/frame (false-positive bound 0.10) |
| Slow-flow (v≤0.2) pass | 22/24 |
| Fast-flow (v≥2) pass | 1/24 (systematic underestimation) |

## Pass rate by true velocity (v>0; 24 conditions each)

| v (px/frame) | pass |
|---|---|
| 0.2 | 91.7% |
| 0.5 | 12.5% |
| 1.0 | 25.0% |
| 2.0 | 4.2% |
| 3.0 | 0.0% |

## Pass rate by factor (v>0)

| Width px | pass | | Contrast | pass | | Noise σ | pass | | Drift | pass |
|---|---|---|---|---|---|---|---|---|---|
| 4 | 15.0% | | 15 | 23.3% | | 3 | 30.0% | | 0.0 | 28.3% |
| 8 | 20.0% | | 40 | 30.0% | | 6 | 23.3% | | 0.5 | 25.0% |
| 12 | 45.0% | | | | | | | | | |

## Working-regime pivot (C=40, σ=3, drift=0.5 — closest to real video)

| v_true | w=4 | w=8 | w=12 |
|---|---|---|---|
| 0.0 | 0.047 ✓ | 0.033 ✓ | 0.060 ✓ |
| 0.2 | 0.092 ✗ | 0.120 ✓ | 0.153 ✓ |
| 0.5 | 0.217 ✗ | 0.295 ✗ | 0.393 ✓ |
| 1.0 | 0.400 ✗ | 0.595 ✗ | 0.774 ✓ |
| 2.0 | 0.718 ✗ | 1.066 ✗ | 1.454 ✗ |
| 3.0 | 1.380 ✗ | 1.673 ✗ | 2.137 ✗ |

(cells = v_rec px/frame; ✓ = pass) — at the observed working regime the envelope
indicates 43–77% recovery of true velocity depending on width; reported
velocities are conservative lower bounds.

## Interpretation guardrails

- The envelope characterises **where the estimator is reliable**, not a
  leaderboard to maximise: any estimator that "wins" by inflating fast-flow
  estimates trades off zero-flow false positives, which the criterion penalises.
- Saturation at fast flow is an expected property of single-frame-pair
  orientation (half-scale video); recovery ratios are width-dependent.
- The between-clip comparison of the manuscript's real-video demonstration is
  explicitly not interpretable; only within-clip performance is claimed there.
