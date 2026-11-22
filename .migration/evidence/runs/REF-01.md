# Run journal: REF-01

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T04:22:42+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:23:28+00:00 | refactor-red | 2 | 3.93 | `pytest -q tests/data_migration/test_export.py` | `c2ec8b1d2cb022ec` | _____________ ERROR collecting tests/data_migration/test_export.py _____________ |  |
| 2026-11-22T04:23:49+00:00 | behavior-focused | 0 | 2.25 | `pytest -q tests/data_migration/test_export.py` | `cd1a1d7624dff51b` |  |  |
| 2026-11-22T04:25:06+00:00 | build-compile | 0 | 0.08 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:25:06+00:00 | build-django | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T04:25:06+00:00 | idiom-ruff | 1 | 0.03 | `ruff check` | `8bf2f5b75f465631` | Found 1 error. |  |
| 2026-11-22T04:25:13+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T04:25:13+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `b221fa32ed80fb2e` |  |  |
| 2026-11-22T04:25:13+00:00 | idiom-layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `59bfd54275a9b5a4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-22T04:25:14+00:00 | idiom-ui | 0 | 0.68 | `python .migration/harness/tools/check_ui.py` | `0ef885e0359232fc` |  | gate=ui scope="templates changed since 2746285675ca82e6844a0f7af25821723cccea9d" templates=0 findings=0 |
| 2026-11-22T04:26:28+00:00 | behavior | 0 | 74.11 | `pytest -q` | `641bb81fa1f602cb` |  |  |
| 2026-11-22T04:28:36+00:00 | crap-coverage | 0 | 70.32 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `663f748941df5070` |  |  |
| 2026-11-22T04:28:36+00:00 | crap-lizard | 0 | 0.16 | `lizard --csv src` | `e9072c81f2aaa826` | 16,3,86,6,16,"_origin_step@38-53@src/cargotracker/booking/interfaces/wizard/views.py","src/cargotracker/booking/interfac |  |
| 2026-11-22T04:28:36+00:00 | crap-score | 0 | 0.2 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `049badc57b42932f` |  | gate=crap max=26.0 threshold=30 over=0 methods=213 |
| 2026-11-22T04:29:59+00:00 | mutation-changed | 0 | 79.34 | `python .migration/harness/tools/afs-mutation` | `177b78fc7ff42ea1` |  | gate=mutation score=0.978 threshold=0.8 killed=90 survived=2 files=2 base=2746285675ca82e6844a0f7af25821723cccea9d |
| 2026-11-22T04:31:16+00:00 | regression | 0 | 70.81 | `pytest -q` | `6f199c4bb75f70e1` |  |  |
