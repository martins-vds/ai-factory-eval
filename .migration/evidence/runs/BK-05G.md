# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T05:46:18+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T05:49:49+00:00 | dialogs-red | 2 | 2.67 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `96729082da183e28` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-15T05:51:07+00:00 | dialogs-focused | 1 | 4.4 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a9cb86fea7af4f58` | assert cargo is not None |  |
| 2026-11-15T05:51:25+00:00 | dialogs-focused | 0 | 4.41 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `80af80970fdfd16d` |  |  |
| 2026-11-15T05:51:53+00:00 | dashboard-dialog-regression | 0 | 5.61 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_dialogs.py` | `48d84e018d2932af` |  |  |
| 2026-11-15T05:52:41+00:00 | dashboard-dialog-regression | 0 | 5.24 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_dialogs.py` | `df32fb810d3750ca` |  |  |
| 2026-11-15T05:54:13+00:00 | idiom-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T05:54:18+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `8339e97ebfd07830` |  |  |
| 2026-11-15T05:54:26+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-15T05:54:41+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T05:54:45+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T05:54:49+00:00 | idiom-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T05:56:00+00:00 | behavior | 0 | 65.24 | `pytest -q` | `0b022ad08005850d` |  |  |
