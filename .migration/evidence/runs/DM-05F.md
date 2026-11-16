# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T17:29:07+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:30:46+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-16T17:32:40+00:00 | fixture-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-16T17:33:08+00:00 | invariant-tests | 1 | 3.54 | `pytest -q tests/data_migration/test_invariants.py` | `ea06bcdf8e584a52` | E           TypeError: A handling activity requires a location |  |
| 2026-11-16T17:33:32+00:00 | invariant-tests | 1 | 1.72 | `pytest -q tests/data_migration/test_invariants.py` | `1baff2dcecfc2bc4` | assert cargos |  |
| 2026-11-16T17:33:40+00:00 | invariant-tests | 0 | 1.71 | `pytest -q tests/data_migration/test_invariants.py` | `14966a85db57e41f` |  |  |
