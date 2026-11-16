# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:00:29+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:05:03+00:00 | behavior-red | 2 | 4.67 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `00ac5477356d0c29` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-16T02:05:59+00:00 | behavior-dialogs | 1 | 3.66 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8f626c7e6699a48b` | assert cargo is not None |  |
| 2026-11-16T02:06:21+00:00 | behavior-dialogs | 0 | 3.54 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `39485e0e80021eb0` |  |  |
| 2026-11-16T02:07:14+00:00 | behavior-booking-ui | 0 | 4.92 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `cdd7b328afebd750` |  |  |
