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
| 2026-11-16T17:36:44+00:00 | crap-coverage | 0 | 49.35 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `ff79c7ab338a49b5` |  |  |
| 2026-11-16T17:36:48+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:36:51+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `b380148b776009c7` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-16T17:39:12+00:00 | mutation-changed | 1 | 137.38 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `458b2e1f89294feb` | afs-mutation: FAILED score=0.639 threshold=0.8 killed=39 survived=22 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.639 threshold=0.8 killed=39 survived=22 files=1 base=origin/main |
| 2026-11-16T17:40:16+00:00 | behavior-mutation-fixes | 0 | 7.01 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `6a55bd8361425ffd` |  |  |
| 2026-11-16T17:40:24+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T17:40:24+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-16T17:42:36+00:00 | mutation-changed-final | 0 | 128.67 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `872139fa2f3fbd9b` |  | gate=mutation score=0.948 threshold=0.8 killed=55 survived=3 files=1 base=origin/main |
| 2026-11-16T17:43:08+00:00 | behavior-exact-errors | 0 | 5.99 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `1ffa7ea82dbbb4af` |  |  |
| 2026-11-16T17:44:12+00:00 | tests-final | 0 | 50.62 | `pytest -q` | `0d7a30fee2d8bd9c` |  |  |
| 2026-11-16T17:44:17+00:00 | build-compile-final | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:44:18+00:00 | build-django-check-final | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T17:44:18+00:00 | idiom-ruff-check-final2 | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T17:44:18+00:00 | idiom-ruff-format-final2 | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-16T17:45:13+00:00 | crap-coverage-final | 0 | 50.8 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `84ea13acd7de7fa5` |  |  |
| 2026-11-16T17:45:17+00:00 | crap-lizard-final | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:45:17+00:00 | crap-score-final | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `37583b244ac6ac34` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-16T17:47:28+00:00 | mutation-changed-final2 | 0 | 126.75 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `9c1b887c6b2c341b` |  | gate=mutation score=1.000 threshold=0.8 killed=58 survived=0 files=1 base=origin/main |
