# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T13:21:07+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:23:29+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-18T13:25:21+00:00 | invariants-tests | 0 | 3.63 | `pytest -q tests/data_migration/test_invariants.py` | `2adbb35b08f0583e` |  |  |
| 2026-11-18T13:25:40+00:00 | build-compileall | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:25:41+00:00 | build-django-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T13:25:45+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `a3cfeff3888b2f4a` | 204 \|         assert legs |  |
| 2026-11-18T13:26:04+00:00 | invariants-tests | 0 | 1.9 | `pytest -q tests/data_migration/test_invariants.py` | `846f06875c7c84ed` |  |  |
| 2026-11-18T13:26:04+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T13:26:04+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T13:26:05+00:00 | idiom-layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T13:26:05+00:00 | idiom-ui | 0 | 0.39 | `python .migration/harness/tools/check_ui.py` | `617c55c57b113cf8` |  | gate=ui scope="templates changed since 884612afff7c2c399300b72816e2b6fd75be8054" templates=0 findings=0 |
