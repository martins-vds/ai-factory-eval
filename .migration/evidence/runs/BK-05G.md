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
| 2026-11-21T22:46:24+00:00 | ruff-check | 1 | 0.02 | `ruff check` | `3bec43a70de0a6b4` | Found 1 error. |  |
| 2026-11-21T22:46:31+00:00 | ruff-fix | 0 | 0.01 | `ruff check --fix tests/booking/interfaces/test_dialogs.py` | `aac3a0503d8b9505` | Found 1 error (1 fixed, 0 remaining). |  |
| 2026-11-21T22:46:35+00:00 | ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T22:46:37+00:00 | ruff-format | 1 | 0.02 | `ruff format --check` | `723e94aa76844915` | 272 \|     assert cargo_after.route_specification.origin == cargo_before.route_specification.origin |  |
| 2026-11-21T22:46:40+00:00 | format-fix | 0 | 0.01 | `ruff format tests/booking/interfaces/test_dialogs.py` | `413a709001976657` |  |  |
| 2026-11-21T22:46:42+00:00 | ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T22:46:52+00:00 | dialogs-e2e | 0 | 5.77 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `96907f08a34afe3d` |  |  |
| 2026-11-21T22:46:54+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T22:46:57+00:00 | build-django-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T22:46:59+00:00 | layers | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T22:47:03+00:00 | ui-check | 0 | 0.52 | `python .migration/harness/tools/check_ui.py` | `ed2097a95ff239c0` |  | gate=ui scope="templates changed since b773736ccfce81b6efe150bd40331263565175d5" templates=4 findings=0 |
