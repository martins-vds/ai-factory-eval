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
| 2026-11-18T12:48:22+00:00 | mutation-changed | 1 | 109.01 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `fefdf194184aca01` | afs-mutation: FAILED score=0.648 threshold=0.8 killed=46 survived=25 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.648 threshold=0.8 killed=46 survived=25 files=1 base=origin/main |
| 2026-11-18T12:51:02+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:52:15+00:00 | behavior-dialog-boundaries | 0 | 3.88 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2454e23acf96015c` |  |  |
| 2026-11-18T12:54:31+00:00 | mutation-changed | 0 | 118.67 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `f1e0b9576945bd53` |  | gate=mutation score=0.845 threshold=0.8 killed=60 survived=11 files=1 base=origin/main |
| 2026-11-18T12:55:23+00:00 | mutation-coverage-probe | 0 | 3.68 | `bash -c 'COVERAGE_FILE=/tmp/bk-05g-dialog-coverage python -m pytest -q -p no:cacheprovider -o addopts= --cov=src --cov-context=test --cov-report= tests/booking/interfaces/test_dialogs.py'` | `49414f99cfb93935` |  |  |
| 2026-11-18T12:56:06+00:00 | idiom-dialog-assertions | 0 | 0.01 | `ruff check tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:56:06+00:00 | format-dialog-assertions | 1 | 0.01 | `ruff format --check tests/booking/interfaces/test_dialogs.py` | `837682230d9f2324` | 237 \|     assert 'value="USDAL"' in _select_options(destination.content.decode()) |  |
| 2026-11-18T12:56:10+00:00 | behavior-dialog-assertions | 0 | 3.97 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `36308943e37e1d73` |  |  |
| 2026-11-18T12:56:15+00:00 | format-dialog-assertions-fix | 0 | 0.01 | `ruff format tests/booking/interfaces/test_dialogs.py` | `413a709001976657` |  |  |
| 2026-11-18T12:56:19+00:00 | idiom-dialog-final | 0 | 0.01 | `ruff check tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:56:19+00:00 | format-dialog-final | 0 | 0.01 | `ruff format --check tests/booking/interfaces/test_dialogs.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-18T12:56:23+00:00 | behavior-dialog-final | 0 | 4.05 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `cc69e7e3db4d0a13` |  |  |
