# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T22:34:46+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T22:37:22+00:00 | invariants | 1 | 4.3 | `pytest -q tests/data_migration/test_invariants.py` | `0b6788c4ee094105` | E           ValueError: Voyage is not allowed with event type RECEIVE |  |
| 2026-11-21T22:37:32+00:00 | invariants | 1 | 2.13 | `pytest -q tests/data_migration/test_invariants.py` | `783450f8ed7e5fcc` | >           assert cargo.delivery == replace(derived, last_event_id=history.most_recent_event_id) |  |
| 2026-11-21T22:37:46+00:00 | invariants | 0 | 2.12 | `pytest -q tests/data_migration/test_invariants.py` | `10e96b85b3bd96cf` |  |  |
