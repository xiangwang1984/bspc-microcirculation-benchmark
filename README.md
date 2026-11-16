# Open dark-field velocity benchmark (144 conditions, bit-exact)

Deterministic phantom + reference table + reproduction gate for microcirculation video
velocity estimation (companion to manuscript TXK6, BSPC submission).

```bash
pip install numpy==2.4.6 opencv-python-headless==5.0.0.93
python run_benchmark.py --check   # 144/144 ALL MATCH
python operating_condition_gate.py
```

CI: `.github/workflows/benchmark-check.yml` (ubuntu + windows). Seed 42. MIT licence.
Provenance: files identical to the archived release layer (14_revision5/open_benchmark_darkfield_velocity;
release_repo_v1.4/benchmark); workflow relocated to repo root with pinned deps, 2026-11-10.
