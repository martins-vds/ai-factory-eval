# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:47:51+00:00 | setup-probe | 0 | 0.01 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:51:12+00:00 | dialogs-red | 2 | 3.55 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `92eea115bd4dfeca` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-19T13:52:15+00:00 | destination-green | 1 | 2.25 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `18bd88a2c447df1f` | assert locations == original_locations |  |
| 2026-11-19T13:52:23+00:00 | destination-green | 0 | 2.03 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `73e52fbff0780f58` |  |  |
| 2026-11-19T13:53:06+00:00 | integration-red | 1 | 3.11 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `13c68dd23bdf9620` | assert cargo is not None |  |
| 2026-11-19T13:53:27+00:00 | dialogs-and-dashboard | 0 | 4.02 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `84ef7238ff42c4c6` |  |  |
| 2026-11-19T13:53:56+00:00 | dialogs-and-dashboard | 0 | 3.79 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `ac3d68313e6a4528` |  |  |
