# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T12:33:05+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:40:19+00:00 | behavior-red | 2 | 2.21 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `96d189e2c964cca8` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T12:41:42+00:00 | behavior-dialogs | 0 | 2.88 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a69fad2d38f69472` |  |  |
| 2026-11-18T12:42:06+00:00 | format-probe | 1 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `8aecc9c52475f917` | 91  \|     assert first_options == second_options |  |
| 2026-11-18T12:42:19+00:00 | behavior-dialogs-formatted | 0 | 2.73 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `82f8b15bda752832` |  |  |
| 2026-11-18T12:42:19+00:00 | ruff-check-probe | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:42:19+00:00 | format-check-probe | 0 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-18T12:42:19+00:00 | ui-check-probe | 0 | 0.26 | `python .migration/harness/tools/check_ui.py` | `d7c99a97f806b1f4` |  | gate=ui scope="templates changed since 9b190a54b0f0e1fcba9c9daa4ad85ce07f4c27c9" templates=3 findings=0 |
| 2026-11-18T12:43:33+00:00 | dialogs-and-dashboard | 0 | 3.24 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `36f129c3f954fea6` |  |  |
| 2026-11-18T12:43:33+00:00 | ui-check-final | 0 | 0.26 | `python .migration/harness/tools/check_ui.py` | `074b6e638d75912f` |  | gate=ui scope="templates changed since 9b190a54b0f0e1fcba9c9daa4ad85ce07f4c27c9" templates=4 findings=0 |
| 2026-11-18T12:44:40+00:00 | build-compileall | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:44:41+00:00 | build-django-check | 0 | 0.22 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T12:44:45+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:44:45+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T12:44:46+00:00 | idiom-layers | 0 | 0.09 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T12:44:46+00:00 | idiom-ui | 0 | 0.26 | `python .migration/harness/tools/check_ui.py` | `074b6e638d75912f` |  | gate=ui scope="templates changed since 9b190a54b0f0e1fcba9c9daa4ad85ce07f4c27c9" templates=4 findings=0 |
| 2026-11-18T12:45:25+00:00 | behavior-regression | 0 | 33.81 | `pytest -q` | `1a6c3afcc8b8d870` |  |  |
| 2026-11-18T12:46:02+00:00 | crap-coverage | 0 | 31.87 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `2da762e90d5ed31f` |  |  |
| 2026-11-18T12:46:02+00:00 | crap-lizard | 0 | 0.08 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:46:02+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `568138dadd34e9db` |  | gate=crap max=26.0 threshold=30 over=0 methods=207 |
