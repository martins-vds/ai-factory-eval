# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:02:43+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:08:30+00:00 | table-red | 1 | 2.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `7b46d3f486b7fc1a` | assert response.status_code == 200 |  |
| 2026-11-17T21:08:46+00:00 | table-green | 0 | 1.89 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `bda5018250507163` |  |  |
