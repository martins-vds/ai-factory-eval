# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:41:20+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:44:15+00:00 | table-actions-red | 1 | 2.66 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_opens_destination_and_deadline_dialogs` | `a0fcb746f97fa8fe` | assert cargo is not None |  |
| 2026-11-22T17:44:28+00:00 | table-actions-green | 0 | 2.24 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_opens_destination_and_deadline_dialogs` | `f71b6d40f60d9414` |  |  |
