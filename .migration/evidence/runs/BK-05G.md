# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:02:43+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:08:30+00:00 | table-red | 1 | 2.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `7b46d3f486b7fc1a` | assert response.status_code == 200 |  |
| 2026-11-17T21:08:46+00:00 | table-green | 0 | 1.89 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `bda5018250507163` |  |  |
| 2026-11-17T21:09:34+00:00 | dialogs-red | 2 | 0.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `618acd581f0d4fb6` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-17T21:10:16+00:00 | dialogs-green | 1 | 3.67 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `3b6301539b820179` | assert cargo is not None |  |
| 2026-11-17T21:10:30+00:00 | dialogs-green | 0 | 3.71 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `1d90be47c8a54e42` |  |  |
| 2026-11-17T21:10:51+00:00 | format-targeted | 1 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `4256d9ffafcc5651` | 78  \|     assert options is not None |  |
| 2026-11-17T21:10:51+00:00 | lint-targeted | 1 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `8b8cac0ee788c878` | Found 1 error. |  |
| 2026-11-17T21:11:08+00:00 | lint-targeted | 1 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `b1bdc3426af7ab95` | Found 1 error. |  |
| 2026-11-17T21:11:08+00:00 | format-targeted | 1 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `e6a09a1d999abf0e` | 78  \|     assert options is not None |  |
| 2026-11-17T21:11:12+00:00 | dialogs-green | 0 | 3.75 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `6aae4cb3848b2348` |  |  |
| 2026-11-17T21:11:35+00:00 | format-diff | 1 | 0.01 | `ruff format --diff tests/booking/interfaces/test_dialogs.py` | `b832bf06efdfe148` | assert options is not None |  |
| 2026-11-17T21:11:35+00:00 | lint-diff | 1 | 0.01 | `ruff check --fix --diff tests/booking/interfaces/test_dialogs.py` | `708d97426db000a0` | Would fix 1 error. |  |
| 2026-11-17T21:11:43+00:00 | lint-targeted | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:11:43+00:00 | format-targeted | 1 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `37d5885b4bb0016d` | 77 \|     assert options is not None |  |
| 2026-11-17T21:11:46+00:00 | dialogs-green | 0 | 3.82 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `7ab97723726f01f7` |  |  |
| 2026-11-17T21:12:01+00:00 | lint-targeted | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:12:01+00:00 | format-targeted | 0 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-17T21:12:04+00:00 | dialogs-green | 0 | 3.81 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ad4dc636c010c6b7` |  |  |
