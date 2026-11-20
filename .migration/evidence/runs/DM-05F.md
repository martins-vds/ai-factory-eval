# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-20T00:34:40+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:35:59+00:00 | snapshot-check | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-20T00:38:20+00:00 | delivery-invariant-red | 0 | 1.48 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_cargo_delivery_state_matches_its_handling_history` | `ab19f6473f2f72d9` |  |  |
| 2026-11-20T00:39:12+00:00 | invariants-tests | 0 | 1.37 | `pytest -q tests/data_migration/test_invariants.py` | `b72ff9de67279024` |  |  |
| 2026-11-20T00:39:54+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:39:54+00:00 | build-check | 0 | 0.26 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T00:39:54+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `4c74f524bdbc921e` |  |  |
| 2026-11-20T00:40:27+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:40:27+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `76aa0a776e7b042c` |  |  |
| 2026-11-20T00:40:36+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-20T00:40:36+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:40:38+00:00 | invariants-tests-final | 0 | 1.31 | `pytest -q tests/data_migration/test_invariants.py` | `cb1a715d9942259c` |  |  |
