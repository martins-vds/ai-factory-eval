# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T13:42:45+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T13:44:37+00:00 | invariants-focused | 1 | 2.51 | `pytest -q tests/data_migration/test_invariants.py` | `1df56ec50d90abff` | E           TypeError: A handling activity requires a location |  |
| 2026-11-15T13:46:00+00:00 | invariants-focused | 0 | 2.18 | `pytest -q tests/data_migration/test_invariants.py` | `578cebb7a3c297c1` |  |  |
