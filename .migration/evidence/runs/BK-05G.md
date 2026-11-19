# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T13:47:37+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:50:51+00:00 | behavior-red | 2 | 3.05 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `d1e6b065bece3242` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-19T13:51:45+00:00 | behavior-dialogs | 1 | 4.5 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `7e3b8f1e612472c7` | assert 'CNHKG' not in options |  |
| 2026-11-19T13:52:00+00:00 | behavior-dialogs | 0 | 4.3 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `132efd337b0c8ab8` |  |  |
| 2026-11-19T13:52:36+00:00 | lint-check | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T13:52:36+00:00 | format-check | 1 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `6d0e33c9f94032e6` | 99  \|     assert updated.route_specification.origin == original.route_specification.origin |  |
| 2026-11-19T13:53:40+00:00 | behavior-dialogs-final | 0 | 4.28 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c8834e6ba7bf08dd` |  |  |
| 2026-11-19T13:53:40+00:00 | layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T13:53:40+00:00 | ui-check | 0 | 0.5 | `python .migration/harness/tools/check_ui.py` | `06b017a801dbbc41` |  | gate=ui scope="templates changed since f4a321e32b3e9774e62d6e26e215bb713d950221" templates=2 findings=0 |
| 2026-11-19T13:54:33+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:54:34+00:00 | build-django-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T13:54:34+00:00 | idiom-ruff | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T13:54:34+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T13:54:34+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T13:54:35+00:00 | idiom-ui | 0 | 0.53 | `python .migration/harness/tools/check_ui.py` | `bd8ca62d2470324c` |  | gate=ui scope="templates changed since f4a321e32b3e9774e62d6e26e215bb713d950221" templates=3 findings=0 |
| 2026-11-19T13:55:38+00:00 | regression | 0 | 60.2 | `pytest -q` | `05be5a560b222f28` |  |  |
| 2026-11-19T13:56:47+00:00 | crap-coverage | 0 | 60.72 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `5d464208aaada7a7` |  |  |
| 2026-11-19T13:56:48+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:56:48+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `7d15457eb2ff0bcf` |  | gate=crap max=26.0 threshold=30 over=0 methods=204 |
| 2026-11-19T13:58:47+00:00 | mutation-changed | 1 | 116.07 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `d21aa659b7c24b73` | afs-mutation: FAILED score=0.681 threshold=0.8 killed=32 survived=15 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.681 threshold=0.8 killed=32 survived=15 files=1 base=origin/main |
