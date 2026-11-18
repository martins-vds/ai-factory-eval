# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T13:46:19+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:50:58+00:00 | invariants-focused | 0 | 2.77 | `pytest -q tests/data_migration/test_invariants.py` | `19bf857b2a3d9624` |  |  |
| 2026-11-18T13:51:41+00:00 | build-compileall | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:51:54+00:00 | build-check | 0 | 0.4 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T13:51:56+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T13:51:59+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T13:52:02+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T13:52:06+00:00 | idiom-ui | 0 | 0.52 | `python .migration/harness/tools/check_ui.py` | `5314bde32c5405da` |  | gate=ui scope="templates changed since faad11837d0c5044abccc8f1b1832853c5e39ec5" templates=0 findings=0 |
| 2026-11-18T13:53:04+00:00 | behavior-regression | 0 | 53.68 | `pytest -q` | `796879b658d38455` |  |  |
| 2026-11-18T13:54:10+00:00 | crap-coverage | 0 | 62.34 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `eff5217454bd50f1` |  |  |
| 2026-11-18T13:54:13+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:54:16+00:00 | crap-score | 0 | 0.05 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-18T13:54:20+00:00 | mutation-changed | 0 | 0.09 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-18T13:57:24+00:00 | regression-final | 0 | 53.92 | `pytest -q` | `fabac3df6f54d217` |  |  |
| 2026-11-18T15:43:47+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T15:45:45+00:00 | idiom-ruff | 0 | 0.11 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T15:45:45+00:00 | idiom-format | 0 | 0.07 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T15:45:45+00:00 | build-compileall | 0 | 0.26 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T15:45:45+00:00 | idiom-layers | 0 | 0.26 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T15:45:45+00:00 | idiom-ui | 0 | 0.58 | `python .migration/harness/tools/check_ui.py` | `5314bde32c5405da` |  | gate=ui scope="templates changed since faad11837d0c5044abccc8f1b1832853c5e39ec5" templates=0 findings=0 |
| 2026-11-18T15:45:46+00:00 | build-check | 0 | 0.74 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T15:46:55+00:00 | behavior | 0 | 48.4 | `pytest -q` | `c345cc494324aec8` |  |  |
| 2026-11-18T15:48:25+00:00 | crap-coverage | 0 | 46.46 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `5979ce74e6b0180a` |  |  |
| 2026-11-18T15:50:22+00:00 | crap-lizard | 0 | 0.17 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T15:52:27+00:00 | crap-score | 0 | 0.06 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
