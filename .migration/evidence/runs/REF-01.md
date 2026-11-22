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
