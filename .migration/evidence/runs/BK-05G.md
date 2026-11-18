# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:36:54+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:40:10+00:00 | dialogs-red | 2 | 2.73 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c901868299d894a6` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T13:41:19+00:00 | dialogs-targeted | 1 | 4.45 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c45d0dc774bf7716` | E       IndexError: list index out of range |  |
| 2026-11-18T13:41:34+00:00 | dialogs-targeted | 2 | 1.05 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `eb25dcfd79055457` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T13:41:45+00:00 | dialogs-targeted | 1 | 4.37 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `31b11f0c7d2d9c26` | assert response.status_code == 200 |  |
| 2026-11-18T13:42:20+00:00 | dialogs-targeted | 0 | 4.37 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `3539f262acf29f0e` |  |  |
| 2026-11-18T13:43:00+00:00 | dialogs-targeted | 0 | 4.86 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2813771d2a0d963d` |  |  |
