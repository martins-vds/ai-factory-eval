# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T20:33:09+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:37:05+00:00 | dialogs-red | 2 | 2.94 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8a93686ce1817765` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
