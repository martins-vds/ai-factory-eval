# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:08:22+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:11:54+00:00 | not-routed-dialogs-red | 1 | 3.32 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `bd6233e2ba78cad5` | assert response.status_code == 200 |  |
| 2026-11-18T03:12:06+00:00 | not-routed-dialogs-green | 0 | 1.77 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `3c243acc54e1579e` |  |  |
