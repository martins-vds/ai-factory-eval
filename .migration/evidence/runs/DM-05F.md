# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T01:35:12+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:38:11+00:00 | invariants-tests | 1 | 4.74 | `pytest -q tests/data_migration/test_invariants.py` | `3705e83cb0739c6d` | E           ValueError: Voyage is not allowed with event type RECEIVE |  |
| 2026-11-23T01:38:22+00:00 | invariants-tests | 0 | 2.08 | `pytest -q tests/data_migration/test_invariants.py` | `3c694261c1f3a68b` |  |  |
