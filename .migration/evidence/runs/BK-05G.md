# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T13:08:29+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:11:39+00:00 | dialogs-red | 2 | 2.99 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c901868299d894a6` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-21T13:12:28+00:00 | dialogs-green | 1 | 4.97 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `1341e779f96a59fa` | assert first_response.status_code == 200 |  |
| 2026-11-21T13:12:44+00:00 | dialogs-green-2 | 0 | 4.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `cd0087a16290275a` |  |  |
| 2026-11-21T13:12:56+00:00 | dashboard-regression | 0 | 2.9 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `708feca03f39820e` |  |  |
| 2026-11-21T13:13:24+00:00 | dialogs-final | 0 | 5.24 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `566e29345cd83114` |  |  |
| 2026-11-21T13:13:29+00:00 | dashboard-regression-final | 0 | 2.83 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `2f4844acf2808bec` |  |  |
