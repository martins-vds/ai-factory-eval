# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T15:03:21+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T15:06:29+00:00 | invariants-tests | 1 | 6.56 | `pytest -q tests/data_migration/test_invariants.py` | `7fd98e3b0a8ed682` | >           assert replace(derived, last_event_id=history.most_recent_event_id) == cargo.delivery |  |
| 2026-11-15T15:06:53+00:00 | invariants-tests | 0 | 2.28 | `pytest -q tests/data_migration/test_invariants.py` | `f007a127784409c8` |  |  |
