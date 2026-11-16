# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:00:29+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:05:03+00:00 | behavior-red | 2 | 4.67 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `00ac5477356d0c29` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-16T02:05:59+00:00 | behavior-dialogs | 1 | 3.66 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8f626c7e6699a48b` | assert cargo is not None |  |
| 2026-11-16T02:06:21+00:00 | behavior-dialogs | 0 | 3.54 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `39485e0e80021eb0` |  |  |
| 2026-11-16T02:07:14+00:00 | behavior-booking-ui | 0 | 4.92 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `cdd7b328afebd750` |  |  |
| 2026-11-16T02:07:32+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:07:32+00:00 | build-django-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T02:07:36+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `7d1e8a062392c09e` | Found 1 error. |  |
| 2026-11-16T02:07:42+00:00 | idiom-fix-imports | 0 | 0.01 | `ruff check --fix tests/booking/interfaces/test_dialogs.py` | `aac3a0503d8b9505` | Found 1 error (1 fixed, 0 remaining). |  |
| 2026-11-16T02:07:42+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T02:07:42+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `c4f82e722ea1df9b` |  |  |
| 2026-11-16T02:07:47+00:00 | idiom-format-fix | 0 | 0.01 | `ruff format src/cargotracker/booking/interfaces/dialogs/views.py` | `413a709001976657` |  |  |
| 2026-11-16T02:07:47+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-16T02:08:37+00:00 | behavior | 0 | 46.94 | `pytest -q` | `f8be1f3ff7b4d649` |  |  |
