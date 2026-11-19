# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T14:16:25+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:18:56+00:00 | snapshot-check | 0 | 0.08 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-19T14:20:11+00:00 | delivery-invariant | 0 | 4.25 | `pytest -q tests/data_migration/test_invariants.py` | `27a58a68125c2fbb` |  |  |
| 2026-11-19T14:20:54+00:00 | invariants | 0 | 2.16 | `pytest -q tests/data_migration/test_invariants.py` | `8a5170c47238fc99` |  |  |
