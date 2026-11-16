"""Runtime operating-condition gate for dark-field velocity outputs.

Motivation (manuscript Results, SNR operating-point sweep, Supplementary Table
S40): the released estimator fails both pass criteria in 30/30 phantom
conditions matched to the real clips' measured stripe-SNR, and 25/30 detected
real-clip segments lie below the 8-px validated width regime. The tool
therefore produces plausible-looking numbers precisely where they cannot be
trusted quantitatively. This gate converts that boundary from documentation
into a runtime guard: any consumer of the released pipeline can classify each
per-segment speed as QUANTITATIVE (inside the phantom-validated envelope) or
ORDINAL (outside it) before using it.

Envelope definition (phantom-validated; manuscript Methods "Phantom envelope"):
  - stripe SNR >= snr_threshold (default 1.0; the operating threshold of the
    S40 sweep; the clips' medians 0.76/1.31 straddle it)
  - vessel width >= width_min px (default 8; the validated reference regime)
  - recovered speed <= v_max px/frame (default 1.0; above this the estimator
    is a conservative lower bound only)

Usage:
    from operating_condition_gate import gate_segments
    flags = gate_segments(snrs, widths, speeds)   # lists, one entry per segment
    # each flag: "quantitative" | "ordinal"  (+ reason string)

Deterministic, stdlib-only, no RNG. MIT licence, 27 October 2026 revision
layer, released with the parent benchmark module.
"""
from typing import Iterable, List, Tuple

DEFAULTS = {"snr_threshold": 1.0, "width_min": 8.0, "v_max": 1.0}


def gate_segment(snr: float, width: float, speed: float, **kw) -> Tuple[str, str]:
    """Classify one segment's speed output against the validated envelope."""
    p = dict(DEFAULTS)
    p.update(kw)
    reasons = []
    if snr is not None and snr < p["snr_threshold"]:
        reasons.append(f"stripe-SNR {snr:.2f} < {p['snr_threshold']}")
    if width is not None and width < p["width_min"]:
        reasons.append(f"width {width:.1f}px < {p['width_min']:.0f}px validated regime")
    if speed is not None and speed > p["v_max"]:
        reasons.append(f"speed {speed:.2f} > {p['v_max']} px/frame (lower-bound regime)")
    return ("quantitative", "inside phantom-validated envelope") if not reasons else ("ordinal", "; ".join(reasons))


def gate_segments(snrs: Iterable[float], widths: Iterable[float],
                  speeds: Iterable[float], **kw) -> List[Tuple[str, str]]:
    """Classify per-segment outputs; lengths must match. None skips a check."""
    out = []
    for snr, w, v in zip(snrs, widths, speeds):
        out.append(gate_segment(snr, w, v, **kw))
    return out


def summarise(flags: List[Tuple[str, str]]) -> dict:
    n_q = sum(1 for f, _ in flags if f == "quantitative")
    return {"n_segments": len(flags), "n_quantitative": n_q,
            "n_ordinal": len(flags) - n_q,
            "fraction_ordinal": round(1 - n_q / len(flags), 3) if flags else None}


if __name__ == "__main__":
    # Self-check on the manuscript's archived real-clip medians (illustrative):
    # septic clip median SNR 0.76, control 1.31; median widths 7.6/5.7 px.
    demo = gate_segments([0.76, 1.31], [7.6, 5.7], [0.45, 0.45])
    for (flag, why), snr in zip(demo, [0.76, 1.31]):
        print(f"SNR {snr}: {flag} ({why})")
    print(summarise(demo))
