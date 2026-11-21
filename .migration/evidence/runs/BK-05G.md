# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T13:08:29+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:11:39+00:00 | dialogs-red | 2 | 2.99 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c901868299d894a6` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
