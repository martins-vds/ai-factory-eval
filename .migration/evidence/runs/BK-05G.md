# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T20:33:09+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:37:05+00:00 | dialogs-red | 2 | 2.94 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8a93686ce1817765` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-21T20:38:24+00:00 | dialogs-view-red | 1 | 5.34 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `7bf2c755ba5deb61` | >       assert 'Change destination' in content |  |
| 2026-11-21T20:39:13+00:00 | dialogs-targeted | 0 | 4.76 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c9601526caea5818` |  |  |
| 2026-11-21T20:39:59+00:00 | dialogs-targeted | 0 | 6.78 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `75be333015baf968` |  |  |
| 2026-11-21T20:40:04+00:00 | ui-check | 0 | 0.67 | `python .migration/harness/tools/check_ui.py` | `af6cca03828672e0` |  | gate=ui scope="templates changed since b491ff4233bc289cdda3c2c7fa6163c4a55acd78" templates=4 findings=0 |
| 2026-11-21T20:40:07+00:00 | ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T20:40:09+00:00 | ruff-format | 1 | 0.02 | `ruff format --check` | `ca6ca915a5f83088` | 76 \|     assert 'AUMEL' not in option_values |  |
| 2026-11-21T20:40:16+00:00 | ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T20:42:20+00:00 | dialogs-targeted | 0 | 6.75 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `e775328d13fd99ad` |  |  |
| 2026-11-21T20:42:24+00:00 | ui-check | 0 | 0.64 | `python .migration/harness/tools/check_ui.py` | `9ee0b634c816ea1f` |  | gate=ui scope="templates changed since b491ff4233bc289cdda3c2c7fa6163c4a55acd78" templates=5 findings=0 |
| 2026-11-21T20:43:16+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:43:19+00:00 | build-django-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T20:43:29+00:00 | behavior-dialogs | 0 | 6.64 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `2ef850f287531bdb` |  |  |
| 2026-11-21T20:43:32+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T20:43:34+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T20:43:37+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T20:43:40+00:00 | idiom-ui | 0 | 0.71 | `python .migration/harness/tools/check_ui.py` | `9ee0b634c816ea1f` |  | gate=ui scope="templates changed since b491ff4233bc289cdda3c2c7fa6163c4a55acd78" templates=5 findings=0 |
| 2026-11-21T20:44:47+00:00 | crap-coverage | 0 | 62.8 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `b2b6116780b939b0` |  |  |
| 2026-11-21T20:44:50+00:00 | crap-lizard | 0 | 0.35 | `bash -lc 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:44:53+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0cea1cdfeb73461b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-21T20:46:59+00:00 | mutation-changed | 1 | 122.97 | `python .migration/harness/tools/afs-mutation` | `957b02cfea7728f4` | afs-mutation: FAILED score=0.636 threshold=0.8 killed=28 survived=16 skipped=0 files=1 jobs=1 base=b491ff4233bc289cdda3c | gate=mutation score=0.636 threshold=0.8 killed=28 survived=16 files=1 base=b491ff4233bc289cdda3c2c7fa6163c4a55acd78 |
| 2026-11-21T20:48:00+00:00 | mutation-tests-red-green | 0 | 7.16 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `95fe6476831b87a0` |  |  |
| 2026-11-21T20:48:23+00:00 | mutation-tests-expanded | 0 | 8.12 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `787245bc802e85eb` |  |  |
| 2026-11-21T20:48:37+00:00 | mutation-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T20:48:39+00:00 | mutation-format | 1 | 0.01 | `ruff format --check` | `bd5a626076e790a3` |  |  |
| 2026-11-21T20:48:45+00:00 | mutation-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T20:50:50+00:00 | mutation-changed | 0 | 121.09 | `python .migration/harness/tools/afs-mutation` | `8d409c3df774d72d` |  | gate=mutation score=0.952 threshold=0.8 killed=40 survived=2 files=1 base=b491ff4233bc289cdda3c2c7fa6163c4a55acd78 |
| 2026-11-21T20:51:22+00:00 | behavior-dialogs-final | 0 | 8.02 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `89ca793eb87d8544` |  |  |
| 2026-11-21T20:51:36+00:00 | build-compile-final | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:51:37+00:00 | build-check-final | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T20:51:37+00:00 | idiom-ruff-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T20:51:37+00:00 | idiom-format-final | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T20:51:37+00:00 | idiom-layers-final | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T20:51:38+00:00 | idiom-ui-final | 0 | 0.67 | `python .migration/harness/tools/check_ui.py` | `9ee0b634c816ea1f` |  | gate=ui scope="templates changed since b491ff4233bc289cdda3c2c7fa6163c4a55acd78" templates=5 findings=0 |
| 2026-11-21T20:52:43+00:00 | regression-final | 0 | 61.59 | `pytest -q` | `543fbb6248a48995` |  |  |
| 2026-11-21T20:53:45+00:00 | crap-coverage-final | 0 | 61.16 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `9408b9c5980de1a3` |  |  |
| 2026-11-21T20:53:45+00:00 | crap-lizard-final | 0 | 0.37 | `bash -lc 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:53:45+00:00 | crap-score-final | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0cea1cdfeb73461b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-21T20:55:40+00:00 | mutation-changed-final | 0 | 110.95 | `python .migration/harness/tools/afs-mutation` | `3238ea3623251e3b` |  | gate=mutation score=1.000 threshold=0.8 killed=39 survived=0 files=1 base=b491ff4233bc289cdda3c2c7fa6163c4a55acd78 |
