# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T13:32:00+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T13:37:23+00:00 | dialogs-dashboard-red | 1 | 2.33 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `4adee5ce3d702290` | assert response.status_code == 200 |  |
| 2026-11-16T13:37:52+00:00 | dashboard-opener-green | 0 | 2.8 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `671d7c47eec9947a` |  |  |
| 2026-11-16T13:38:22+00:00 | destination-get-red | 2 | 0.94 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `aa43f32e0ee61d05` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-16T13:39:08+00:00 | destination-get-green | 1 | 2.32 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2844beb86a88f45f` | assert first_response.status_code == 200 |  |
| 2026-11-16T13:39:19+00:00 | destination-get-green-retry | 0 | 2.38 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `219fe1215e473506` |  |  |
| 2026-11-16T13:39:43+00:00 | destination-update | 0 | 2.76 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `6fd24fe56f9c974e` |  |  |
