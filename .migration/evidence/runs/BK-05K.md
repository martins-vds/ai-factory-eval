# Run journal: BK-05K

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T22:04:44+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T22:08:35+00:00 | red | 1 | 5.02 | `pytest -q tests/test_htmx_errors.py` | `24b0bae78b65fbf7` | assert response.status_code == 500 |  |
| 2026-11-18T22:08:55+00:00 | red-corrected | 1 | 4.16 | `pytest -q tests/test_htmx_errors.py` | `b5ca78e982bcdc5c` | assert response.status_code == 500 |  |
