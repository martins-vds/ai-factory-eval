# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T05:55:04+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T05:56:33+00:00 | fixture-snapshot-check | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-16T05:58:44+00:00 | invariants-focused | 0 | 3.13 | `pytest -q tests/data_migration/test_invariants.py` | `aad2405d7cd17123` |  |  |
| 2026-11-16T05:59:13+00:00 | invariants-focused-final | 0 | 1.28 | `pytest -q tests/data_migration/test_invariants.py` | `6d62fa340acc13b4` |  |  |
