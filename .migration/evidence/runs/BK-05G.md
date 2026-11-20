# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:34:42+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:38:24+00:00 | dialogs-red-table | 1 | 2.79 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a202bd45c665cac4` | assert cargo is not None |  |
| 2026-11-20T00:38:46+00:00 | dialogs-green-table | 0 | 2.29 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `488b55d0b06d1251` |  |  |
| 2026-11-20T00:40:06+00:00 | dialogs-red-views | 2 | 1.08 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `b57025eeed794451` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-20T00:40:42+00:00 | dialogs-tests | 1 | 2.35 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0760d4a3a2c4c708` | _ ERROR at setup of test_not_routed_table_opens_destination_and_deadline_dialogs _ |  |
| 2026-11-20T00:40:56+00:00 | dialogs-tests | 0 | 6.63 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `4aacc64bf85b7490` |  |  |
| 2026-11-20T00:41:10+00:00 | dashboard-regression | 0 | 7.9 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_dialogs.py` | `49bcda0ac892ac1c` |  |  |
