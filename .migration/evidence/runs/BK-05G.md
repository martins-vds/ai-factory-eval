# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T22:38:11+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T22:43:13+00:00 | dialogs-red | 2 | 1.33 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `74d2ff40db76c3cc` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-21T22:44:23+00:00 | dialogs-focused | 0 | 4.17 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `cb3a674306b64774` |  |  |
| 2026-11-21T22:44:32+00:00 | dashboard-regression | 0 | 5.19 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `1f9aaea92c7f31f6` |  |  |
| 2026-11-21T22:45:45+00:00 | dialogs-e2e | 0 | 5.74 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `35ee3415f353cf4d` |  |  |
