# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:29:01+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:31:53+00:00 | tests-red | 2 | 1.18 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `e6005f2ec8a65724` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-16T17:32:57+00:00 | behavior-targeted | 0 | 5.11 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `77f27cd98e065595` |  |  |
| 2026-11-16T17:34:15+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T17:34:15+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `1dd11ef7b8f67878` |  |  |
| 2026-11-16T17:34:24+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-16T17:34:24+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:34:24+00:00 | build-django-check | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T17:35:20+00:00 | tests | 0 | 52.0 | `pytest -q` | `86f26c67e0b89ef9` |  |  |
