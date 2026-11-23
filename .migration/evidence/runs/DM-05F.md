# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T00:43:54+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:44:48+00:00 | snapshot-check | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-23T00:47:20+00:00 | invariants | 0 | 4.01 | `pytest -q tests/data_migration/test_invariants.py` | `593ffc4878763a58` |  |  |
| 2026-11-23T00:47:33+00:00 | ruff-check | 1 | 0.02 | `ruff check` | `f70d8d5aa1b2fd12` | 214 \|             assert movement.departure_time < movement.arrival_time |  |
| 2026-11-23T00:47:33+00:00 | ruff-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T00:47:34+00:00 | invariants | 0 | 1.29 | `pytest -q tests/data_migration/test_invariants.py` | `a4f90380a50f47a8` |  |  |
| 2026-11-23T00:47:41+00:00 | ruff-check | 1 | 0.01 | `ruff check` | `d9a983064f4b09fd` | Found 1 error. |  |
| 2026-11-23T00:47:41+00:00 | ruff-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T00:47:43+00:00 | invariants | 0 | 1.21 | `pytest -q tests/data_migration/test_invariants.py` | `e1e76aa649e63250` |  |  |
| 2026-11-23T00:47:49+00:00 | ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:47:49+00:00 | ruff-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T00:47:50+00:00 | invariants | 0 | 1.21 | `pytest -q tests/data_migration/test_invariants.py` | `ace756f276043610` |  |  |
