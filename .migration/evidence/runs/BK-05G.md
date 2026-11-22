# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:40:11+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:43:48+00:00 | dialogs-red | 2 | 3.06 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `d40dbd9c677d6847` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-22T17:44:58+00:00 | dialogs-targeted | 1 | 4.48 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `30260f25f044a078` | assert cargo is not None |  |
| 2026-11-22T17:45:15+00:00 | dialogs-targeted | 0 | 4.22 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `dc7e08367c35089d` |  |  |
| 2026-11-22T17:46:20+00:00 | dialogs-targeted | 0 | 4.93 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `aae4acc193d409eb` |  |  |
