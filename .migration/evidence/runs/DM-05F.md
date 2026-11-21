# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T18:59:38+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T19:02:54+00:00 | delivery-invariant-red | 1 | 2.39 | `pytest -q tests/data_migration/test_invariants.py` | `7f90152f3fc1a26f` | E           TypeError: A handling activity requires a location |  |
| 2026-11-21T19:03:35+00:00 | invariants-targeted | 0 | 2.28 | `pytest -q tests/data_migration/test_invariants.py` | `624e8ca77d788c89` |  |  |
| 2026-11-21T19:04:03+00:00 | invariants-red-green | 0 | 2.26 | `pytest -q tests/data_migration/test_invariants.py` | `4dc6033adb5540b5` |  |  |
| 2026-11-21T19:04:32+00:00 | data-migration-tests | 0 | 6.21 | `pytest -q tests/data_migration` | `f2a7af5dd6023948` |  |  |
| 2026-11-21T19:04:47+00:00 | ruff-check | 1 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `e48e7cba78b55cfe` |  |  |
| 2026-11-21T19:04:54+00:00 | ruff-check | 0 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T19:04:54+00:00 | ruff-format | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-21T19:04:54+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T19:04:54+00:00 | build-check | 0 | 0.4 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T19:05:25+00:00 | snapshot-fixture-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
