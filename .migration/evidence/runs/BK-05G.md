# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:28:47+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:32:07+00:00 | dialogs-red | 2 | 2.53 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2bfec778546d61b5` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-16T15:33:03+00:00 | dialogs-green | 1 | 2.59 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `f1dffbe06e18da6d` | assert cargo is not None |  |
| 2026-11-16T15:33:27+00:00 | dialogs-targeted | 0 | 2.81 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `402bdb771b4bdad7` |  |  |
| 2026-11-16T15:33:32+00:00 | dashboard-regression | 0 | 1.71 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `1fedb9e39f8abcf0` |  |  |
| 2026-11-16T15:34:04+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T15:34:07+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `9900200fa6b7d48c` | 66  \|     assert cargo is not None |  |
| 2026-11-16T15:34:15+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-16T15:34:22+00:00 | dialogs-targeted | 0 | 3.4 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `bf52e4e51d0f2814` |  |  |
| 2026-11-16T15:35:30+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:35:35+00:00 | build-django-check | 0 | 0.25 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T15:36:28+00:00 | crap-pytest | 0 | 37.45 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `8371361e50eab648` |  |  |
| 2026-11-16T15:36:33+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:36:37+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `3edcf2afb9479501` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-16T15:38:26+00:00 | mutation-changed | 1 | 104.73 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `d7517fdc86cc8d24` | afs-mutation: FAILED score=0.613 threshold=0.8 killed=38 survived=24 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.613 threshold=0.8 killed=38 survived=24 files=1 base=origin/main |
| 2026-11-16T15:39:59+00:00 | mutation-tests | 0 | 3.9 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `016ef25e9f766e78` |  |  |
| 2026-11-16T15:40:28+00:00 | mutation-tests | 0 | 4.69 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `9083e07e3f41f1a3` |  |  |
| 2026-11-16T15:42:14+00:00 | mutation-changed | 0 | 99.23 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `3bce5d5dc5024904` |  | gate=mutation score=0.917 threshold=0.8 killed=55 survived=5 files=1 base=origin/main |
| 2026-11-16T15:44:24+00:00 | mutation-tests | 0 | 4.22 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `f38e11e4bbdded21` |  |  |
| 2026-11-16T15:46:01+00:00 | mutation-changed | 0 | 92.34 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `818a3af1c86d107b` |  | gate=mutation score=0.917 threshold=0.8 killed=55 survived=5 files=1 base=origin/main |
| 2026-11-16T15:46:32+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:46:36+00:00 | build-django-check | 0 | 0.26 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T15:46:40+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T15:46:44+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-16T15:47:27+00:00 | crap-pytest | 0 | 39.58 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `cccbaa33c041b2c4` |  |  |
| 2026-11-16T15:47:31+00:00 | crap-lizard | 0 | 0.1 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:47:35+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0450619388611d7f` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-16T15:48:53+00:00 | behavior-regression | 0 | 38.84 | `pytest -q` | `4d962101665bcbf6` |  |  |
| 2026-11-16T15:53:25+00:00 | nojs-red | 4 | 0.62 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_dialogs_support_full_page_forms_without_javascript` | `487da005e163f161` | ERROR: found no collectors for /home/runner/work/ai-factory-eval/ai-factory-eval/tests/booking/interfaces/test_dialogs.p |  |
| 2026-11-16T15:53:46+00:00 | nojs-red | 1 | 1.5 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_dialogs_support_full_page_forms_without_javascript` | `e8c5b859bdd50f28` | assert cargo is not None |  |
| 2026-11-16T15:54:12+00:00 | nojs-green | 0 | 1.59 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_dialogs_support_full_page_forms_without_javascript` | `dc865d24518196dc` |  |  |
| 2026-11-16T15:54:22+00:00 | dialogs-targeted | 0 | 5.45 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `aa30fc354215f9a4` |  |  |
| 2026-11-16T15:54:40+00:00 | dialogs-targeted | 0 | 5.44 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `375b6fff9611b12d` |  |  |
| 2026-11-16T15:54:52+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:54:57+00:00 | build-django-check | 0 | 0.25 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T15:55:02+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T15:55:07+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-16T15:55:50+00:00 | crap-pytest | 0 | 39.57 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `6c241aeaa7522c9e` |  |  |
| 2026-11-16T15:55:56+00:00 | crap-lizard | 0 | 0.1 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:56:04+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `251a5145aa44243b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-16T16:19:33+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
