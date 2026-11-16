# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T13:32:56+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T13:35:49+00:00 | data-snapshot | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-16T13:37:06+00:00 | invariants-delivery | 1 | 4.92 | `pytest -q tests/data_migration/test_invariants.py` | `3ca06a0aa1093202` | >           assert cargo.delivery == replace(expected, last_event_id=history.most_recent_event_id) |  |
| 2026-11-16T13:37:26+00:00 | invariants-delivery | 0 | 1.66 | `pytest -q tests/data_migration/test_invariants.py` | `7bc5776d19eed069` |  |  |
| 2026-11-16T13:37:45+00:00 | invariants | 0 | 2.17 | `pytest -q tests/data_migration/test_invariants.py` | `578cebb7a3c297c1` |  |  |
| 2026-11-16T13:38:03+00:00 | idiom-ruff-check | 1 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `76037f3e14f4be29` | 184 \|         assert all( |  |
| 2026-11-16T13:38:13+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T13:38:13+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
