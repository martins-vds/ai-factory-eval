# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:45:43+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:51:09+00:00 | behavior-red | 1 | 4.49 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `5fa15ba8125c6b37` | assert response.status_code == 200 |  |
| 2026-11-18T03:51:24+00:00 | behavior-table-actions | 1 | 2.3 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `e3063ff31003e6c2` | assert response.status_code == 200 |  |
| 2026-11-18T03:51:36+00:00 | behavior-table-actions | 0 | 2.3 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `9a777c8cb819b44d` |  |  |
| 2026-11-18T03:52:55+00:00 | behavior-destination-red | 2 | 1.01 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `61bef741f07540ef` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T03:53:54+00:00 | behavior-destination | 0 | 2.79 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `fcd5f4644057ac59` |  |  |
