# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:06:19+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:10:16+00:00 | behavior-red | 2 | 2.55 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c31cbd21411297e4` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T03:11:39+00:00 | behavior-dialogs | 1 | 4.19 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `109e47ab0f3b87b8` | assert first.status_code == 200 |  |
| 2026-11-18T03:11:50+00:00 | behavior-dialogs | 0 | 3.85 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `0d408efeeb7bde02` |  |  |
| 2026-11-18T03:12:31+00:00 | behavior-dialogs | 0 | 3.94 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `c4fbd302596c4753` |  |  |
