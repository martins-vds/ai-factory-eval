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
| 2026-11-16T02:09:44+00:00 | crap-coverage | 0 | 47.12 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `b95ed3d0d13748a8` |  |  |
| 2026-11-16T02:09:45+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:09:45+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `715365ebb2f10522` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-16T02:14:23+00:00 | mutation-changed | 1 | 274.73 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `eea87539f9910475` | afs-mutation: FAILED score=0.760 threshold=0.8 killed=38 survived=12 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.760 threshold=0.8 killed=38 survived=12 files=1 base=origin/main |
| 2026-11-16T02:15:45+00:00 | behavior-dialogs-mutation-cases | 0 | 5.42 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a7eb7dcb1403e203` |  |  |
| 2026-11-16T02:20:44+00:00 | mutation-changed | 0 | 269.36 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `0106126f6196412c` |  | gate=mutation score=0.860 threshold=0.8 killed=43 survived=7 files=1 base=origin/main |
| 2026-11-16T02:21:33+00:00 | behavior-dialogs-final-cases | 0 | 6.37 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `b62c9c880d86c132` |  |  |
| 2026-11-16T02:21:33+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check tests/booking/interfaces/test_dialogs.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T02:26:08+00:00 | mutation-changed | 0 | 254.2 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `ebb05ebd24d1e031` |  | gate=mutation score=0.940 threshold=0.8 killed=47 survived=3 files=1 base=origin/main |
| 2026-11-16T02:27:40+00:00 | behavior-final | 0 | 50.05 | `pytest -q` | `9bf9500c8a9cfb48` |  |  |
| 2026-11-16T02:28:29+00:00 | regression | 0 | 48.6 | `pytest -q` | `88b3bc189031fd26` |  |  |
| 2026-11-16T02:32:31+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:34:30+00:00 | behavior-inherited-select-red | 1 | 1.96 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_opens_dialogs_and_refreshes_after_dialog_completion` | `7cb20516bd4da060` | assert response.status_code == 200 |  |
| 2026-11-16T02:34:44+00:00 | behavior-inherited-select-green | 0 | 1.97 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_opens_dialogs_and_refreshes_after_dialog_completion` | `7edfb975894be936` |  |  |
| 2026-11-16T02:36:45+00:00 | build-compile-final | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:36:45+00:00 | build-django-check-final | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T02:36:45+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T02:36:45+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-16T02:37:41+00:00 | behavior-final-current | 0 | 56.16 | `pytest -q` | `718a26aada627920` |  |  |
| 2026-11-16T02:38:28+00:00 | crap-coverage-final | 0 | 46.39 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `a3ad0d5380d2875e` |  |  |
| 2026-11-16T02:38:28+00:00 | crap-lizard-final | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:38:28+00:00 | crap-score-final | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `715365ebb2f10522` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-16T02:42:23+00:00 | mutation-changed-final | 0 | 235.01 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `ebb05ebd24d1e031` |  | gate=mutation score=0.940 threshold=0.8 killed=47 survived=3 files=1 base=origin/main |
| 2026-11-16T02:43:11+00:00 | regression-final-current | 0 | 48.01 | `pytest -q` | `6ae177b0b0448ed2` |  |  |
