# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T03:00:24+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:02:57+00:00 | snapshot-help | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot --help` | `387e1fc810d4925d` |  |  |
| 2026-11-18T03:03:02+00:00 | snapshot-check | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-18T03:04:28+00:00 | invariants-red-green | 1 | 3.48 | `pytest -q tests/data_migration/test_invariants.py` | `256ce0fddfe08e29` | assert cargoes |  |
| 2026-11-18T03:04:48+00:00 | invariants | 0 | 1.48 | `pytest -q tests/data_migration/test_invariants.py` | `8dcd4ff2b182559e` |  |  |
| 2026-11-18T03:05:00+00:00 | idiom-ruff-check | 1 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `5249f3f465c70822` | 209 \|             assert movement.departure_time <= movement.arrival_time |  |
| 2026-11-18T03:05:09+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T03:05:09+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-18T03:05:40+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:05:41+00:00 | build-check | 0 | 0.26 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T03:05:41+00:00 | idiom-ruff-check-all | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T03:05:41+00:00 | idiom-ruff-format-all | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T03:05:41+00:00 | idiom-layers | 0 | 0.1 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T03:05:41+00:00 | idiom-ui | 0 | 0.29 | `python .migration/harness/tools/check_ui.py` | `2e16617a69bea314` |  | gate=ui scope="templates changed since 01f1f08050b982e5e0fdd5b4e3dfb6bfaec9417f" templates=0 findings=0 |
| 2026-11-18T03:05:43+00:00 | behavior | 0 | 1.39 | `pytest -q tests/data_migration/test_invariants.py` | `b72ff9de67279024` |  |  |
| 2026-11-18T03:06:16+00:00 | regression | 0 | 30.18 | `pytest -q` | `c6009d11bf881c29` |  |  |
