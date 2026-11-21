# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T23:43:31+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:47:03+00:00 | invariants | 0 | 2.5 | `pytest -q tests/data_migration/test_invariants.py` | `eee6ca43739a8141` |  |  |
| 2026-11-21T23:47:44+00:00 | behavior | 0 | 2.09 | `pytest -q tests/data_migration/test_invariants.py` | `578cebb7a3c297c1` |  |  |
