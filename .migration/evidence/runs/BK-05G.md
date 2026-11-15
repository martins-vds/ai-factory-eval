# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T13:42:35+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T13:47:10+00:00 | tests-red | 2 | 3.71 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8a151c74c5e5ab40` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-15T13:48:45+00:00 | tests-focused | 0 | 3.51 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `4a717a5fa9a31e40` |  |  |
| 2026-11-15T13:49:22+00:00 | tests-focused | 0 | 4.24 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `59b133eb456a1c49` |  |  |
| 2026-11-15T13:50:45+00:00 | tests-focused | 0 | 4.21 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `266d6aca6e8ede18` |  |  |
| 2026-11-15T13:51:45+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T13:51:49+00:00 | build-check | 0 | 0.28 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T13:51:52+00:00 | idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T13:51:55+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `fe0b3d56fe10846e` | 146 \|     assert updated.route_specification.destination == destination |  |
| 2026-11-15T13:52:10+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `c3ac60a207092b7f` |  |  |
| 2026-11-15T13:53:00+00:00 | behavior-tests | 0 | 46.27 | `pytest -q` | `38f32a2b5447eefe` |  |  |
| 2026-11-15T13:53:50+00:00 | crap-coverage | 0 | 44.11 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `82691f7a9726b197` |  |  |
| 2026-11-15T13:53:54+00:00 | crap-lizard | 0 | 0.13 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T13:53:57+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `a9f0d9bfbb9351b1` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-15T13:54:46+00:00 | regression-tests | 0 | 44.77 | `pytest -q` | `8d07ab1990fc67af` |  |  |
