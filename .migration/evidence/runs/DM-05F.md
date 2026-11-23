# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T00:44:07+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:44:38+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-23T00:46:16+00:00 | invariants-tests | 0 | 4.08 | `pytest -q tests/data_migration/test_invariants.py` | `f4bcd235d33b5e16` |  |  |
| 2026-11-23T00:46:33+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `01407f15504a11c9` | Found 1 error. |  |
| 2026-11-23T00:46:38+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:46:40+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `283373fc71196684` | 41 \|         assert ( |  |
| 2026-11-23T00:46:46+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T00:46:50+00:00 | invariants-tests | 0 | 1.96 | `pytest -q tests/data_migration/test_invariants.py` | `3d64fcf3ab8423c2` |  |  |
| 2026-11-23T00:46:52+00:00 | build-compileall | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:46:54+00:00 | build-django-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T00:46:57+00:00 | idiom-layers | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-23T00:46:59+00:00 | idiom-ui | 0 | 0.55 | `python .migration/harness/tools/check_ui.py` | `55046f5f854904c6` |  | gate=ui scope="templates changed since c7cca0f46b6a2f6341d49647b27c5ec24d67061c" templates=0 findings=0 |
| 2026-11-23T00:47:47+00:00 | regression-tests | 0 | 45.14 | `pytest -q` | `c2ee65c4e704a432` |  |  |
| 2026-11-23T00:48:32+00:00 | crap-coverage | 0 | 42.71 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `f3ad62d2567d87d2` |  |  |
| 2026-11-23T00:48:35+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:48:37+00:00 | crap-threshold | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-23T00:48:39+00:00 | mutation-changed | 0 | 0.08 | `python .migration/harness/tools/afs-mutation` | `a6c281aaeb3b3a59` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=c7cca0f46b6a2f6341d49647b27c5ec24d67061c |
