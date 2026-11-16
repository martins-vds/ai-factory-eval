# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T05:55:03+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T05:59:19+00:00 | focused-red | 2 | 1.33 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8fc2cc9247cc46e4` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-16T06:00:07+00:00 | focused-green | 1 | 4.18 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `47628a6ca7165cac` | assert original is not None |  |
| 2026-11-16T06:00:23+00:00 | focused-green | 0 | 4.26 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ad8923c4cd1a061f` |  |  |
