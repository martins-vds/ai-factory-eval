# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T21:39:28+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:42:38+00:00 | dialogs-red | 2 | 3.87 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2193dafcd502753b` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-19T21:43:41+00:00 | dialogs-targeted | 1 | 2.84 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ed91df60d0647427` | assert response.status_code == 200 |  |
| 2026-11-19T21:43:52+00:00 | dialogs-targeted | 0 | 2.59 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `29cce0583b56b0ed` |  |  |
| 2026-11-19T21:44:26+00:00 | dialogs-targeted | 0 | 2.77 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `325400f4d722e218` |  |  |
