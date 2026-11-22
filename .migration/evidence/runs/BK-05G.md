# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:20:11+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:24:00+00:00 | dialogs-red | 2 | 1.38 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `313a6d39f55ffb69` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-22T17:25:50+00:00 | dialogs-green | 0 | 4.45 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `e3df911906c5f7a4` |  |  |
