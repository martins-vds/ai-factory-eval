# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T21:39:59+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:43:40+00:00 | invariants-red | 2 | 3.02 | `pytest -q tests/data_migration/test_invariants.py` | `2b4dad968ade4654` | ___________ ERROR collecting tests/data_migration/test_invariants.py ___________ |  |
| 2026-11-19T21:43:51+00:00 | invariants | 1 | 2.22 | `pytest -q tests/data_migration/test_invariants.py` | `f51031e9a9874c56` | assert cargos |  |
| 2026-11-19T21:44:11+00:00 | invariants | 0 | 2.07 | `pytest -q tests/data_migration/test_invariants.py` | `f56eadf3d7746ccb` |  |  |
| 2026-11-19T21:44:46+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:44:46+00:00 | build-check | 0 | 0.37 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T21:44:54+00:00 | behavior | 0 | 2.04 | `pytest -q tests/data_migration/test_invariants.py` | `d3db388f4ecc4e6b` |  |  |
| 2026-11-19T21:44:58+00:00 | idiom-ruff | 1 | 0.03 | `ruff check` | `9bf3f0ebe8b1171c` | 162 \|     assert any(len(legs) > 1 for legs in itineraries) |  |
| 2026-11-19T21:45:07+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T21:45:11+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-19T21:45:11+00:00 | idiom-layers | 0 | 0.15 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T21:45:12+00:00 | idiom-ui | 0 | 0.52 | `python .migration/harness/tools/check_ui.py` | `0e05fa2652cd454e` |  | gate=ui scope="templates changed since 118cb1dc2cb78f949a84849e29cf7e4fb1475103" templates=0 findings=0 |
| 2026-11-19T21:46:07+00:00 | crap-coverage | 0 | 48.57 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `03760fd306167c6d` |  |  |
| 2026-11-19T21:46:07+00:00 | crap-lizard | 0 | 0.14 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:46:08+00:00 | crap-check | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-19T21:46:12+00:00 | mutation-changed | 0 | 0.08 | `python .migration/harness/tools/afs-mutation` | `c22689ae20767327` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=118cb1dc2cb78f949a84849e29cf7e4fb1475103 |
| 2026-11-19T21:47:03+00:00 | regression | 0 | 44.86 | `pytest -q` | `e694b0f167812908` |  |  |
| 2026-11-19T21:52:06+00:00 | behavior-review-fix | 0 | 2.08 | `pytest -q tests/data_migration/test_invariants.py` | `3c694261c1f3a68b` |  |  |
| 2026-11-19T21:52:06+00:00 | build-compile-review-fix | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:52:07+00:00 | build-check-review-fix | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T21:52:11+00:00 | idiom-ruff-review-fix | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T21:52:11+00:00 | idiom-format-review-fix | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-19T21:52:11+00:00 | idiom-layers-review-fix | 0 | 0.15 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T21:52:12+00:00 | idiom-ui-review-fix | 0 | 0.54 | `python .migration/harness/tools/check_ui.py` | `0e05fa2652cd454e` |  | gate=ui scope="templates changed since 118cb1dc2cb78f949a84849e29cf7e4fb1475103" templates=0 findings=0 |
| 2026-11-19T21:53:01+00:00 | crap-coverage-review-fix | 0 | 44.54 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `97a426a4a56d054a` |  |  |
| 2026-11-19T21:53:01+00:00 | crap-lizard-review-fix | 0 | 0.14 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:53:01+00:00 | crap-check-review-fix | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-19T21:53:05+00:00 | mutation-changed-review-fix | 0 | 0.08 | `python .migration/harness/tools/afs-mutation` | `c22689ae20767327` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=118cb1dc2cb78f949a84849e29cf7e4fb1475103 |
| 2026-11-19T21:53:49+00:00 | regression-review-fix | 0 | 43.94 | `pytest -q` | `cb395a5fc2ed86d8` |  |  |
