# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:28:47+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:32:07+00:00 | dialogs-red | 2 | 2.53 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2bfec778546d61b5` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-16T15:33:03+00:00 | dialogs-green | 1 | 2.59 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `f1dffbe06e18da6d` | assert cargo is not None |  |
| 2026-11-16T15:33:27+00:00 | dialogs-targeted | 0 | 2.81 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `402bdb771b4bdad7` |  |  |
| 2026-11-16T15:33:32+00:00 | dashboard-regression | 0 | 1.71 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `1fedb9e39f8abcf0` |  |  |
| 2026-11-16T15:34:04+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T15:34:07+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `9900200fa6b7d48c` | 66  \|     assert cargo is not None |  |
| 2026-11-16T15:34:15+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-16T15:34:22+00:00 | dialogs-targeted | 0 | 3.4 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `bf52e4e51d0f2814` |  |  |
