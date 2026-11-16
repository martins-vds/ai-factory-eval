# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T20:36:35+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:39:25+00:00 | fixture-snapshot | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-16T20:40:44+00:00 | invariants | 1 | 3.37 | `pytest -q tests/data_migration/test_invariants.py` | `e4e74d7943cfdbba` | E           ValueError: Voyage is not allowed with event type RECEIVE |  |
| 2026-11-16T20:41:03+00:00 | invariants | 0 | 1.66 | `pytest -q tests/data_migration/test_invariants.py` | `01b439f99d953570` |  |  |
