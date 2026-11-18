# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:40:22+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:43:19+00:00 | behavior-red | 2 | 2.71 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8e9dc4d3d2b73809` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T12:44:52+00:00 | destination-get-green | 0 | 2.41 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `9079c917b3657ef1` |  |  |
| 2026-11-18T12:45:18+00:00 | deadline-get-red | 2 | 0.94 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0da0825529419e67` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T12:45:36+00:00 | deadline-get-green | 0 | 2.71 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `770f62c2fcfb7714` |  |  |
| 2026-11-18T12:46:00+00:00 | deadline-validation-red | 2 | 0.95 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `1ec4f25e9da991e2` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T12:46:26+00:00 | deadline-validation-green | 0 | 3.3 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `16ea4f870f6be017` |  |  |
| 2026-11-18T12:46:52+00:00 | deadline-update-green | 0 | 3.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8e75ad31b1f8847b` |  |  |
