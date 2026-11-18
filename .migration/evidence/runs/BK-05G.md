# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:09:22+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:12:31+00:00 | red-not-routed-dialogs | 1 | 4.11 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `45dc11af28c1fcb9` | assert response.status_code == 200 |  |
| 2026-11-18T13:12:45+00:00 | table-dialog-actions | 0 | 2.25 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ac66644beec34f95` |  |  |
