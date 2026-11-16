# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T13:32:00+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T13:37:23+00:00 | dialogs-dashboard-red | 1 | 2.33 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `4adee5ce3d702290` | assert response.status_code == 200 |  |
| 2026-11-16T13:37:52+00:00 | dashboard-opener-green | 0 | 2.8 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `671d7c47eec9947a` |  |  |
| 2026-11-16T13:38:22+00:00 | destination-get-red | 2 | 0.94 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `aa43f32e0ee61d05` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-16T13:39:08+00:00 | destination-get-green | 1 | 2.32 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2844beb86a88f45f` | assert first_response.status_code == 200 |  |
| 2026-11-16T13:39:19+00:00 | destination-get-green-retry | 0 | 2.38 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `219fe1215e473506` |  |  |
| 2026-11-16T13:39:43+00:00 | destination-update | 0 | 2.76 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `6fd24fe56f9c974e` |  |  |
| 2026-11-16T13:40:21+00:00 | deadline-dialog-red | 1 | 2.17 | `pytest -q tests/booking/interfaces/test_dialogs.py -k deadline_dialog_shows_current_specification_values` | `ec5dfa55d584452b` | assert original is not None |  |
| 2026-11-16T13:40:35+00:00 | deadline-dialog-green | 1 | 3.98 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `377384e1632b338c` | assert original is not None |  |
| 2026-11-16T13:40:47+00:00 | deadline-dialog-green-retry | 0 | 3.98 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `92be2ba3a96322fd` |  |  |
| 2026-11-16T13:42:41+00:00 | dialogs-dashboard-regression | 0 | 5.4 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py tests/booking/application/test_specification.py` | `82ec5288fd4c06c5` |  |  |
| 2026-11-16T13:44:50+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T13:44:50+00:00 | build-django-check | 0 | 0.32 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T13:44:54+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `c3b5e85528bb036c` | Found 1 error. |  |
| 2026-11-16T13:45:01+00:00 | idiom-ruff-check-retry | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T13:45:01+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `5952ac1a2cc036bb` | 133 \|     assert updated.route_specification.destination.unlocode.value == 'USNYC' |  |
| 2026-11-16T13:45:07+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T13:45:07+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-16T13:46:03+00:00 | behavior-tests | 0 | 49.66 | `pytest -q` | `8e51338f51502108` |  |  |
| 2026-11-16T13:48:10+00:00 | crap-coverage | 0 | 47.43 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `13df33405dab55af` |  |  |
| 2026-11-16T13:48:10+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T13:48:10+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `c1c1e749ebed3ef2` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-16T13:49:59+00:00 | mutation-changed | 1 | 101.13 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `8cff6131fd67f869` | afs-mutation: FAILED score=0.783 threshold=0.8 killed=36 survived=10 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.783 threshold=0.8 killed=36 survived=10 files=1 base=origin/main |
| 2026-11-16T13:51:28+00:00 | mutation-survivor-tests | 0 | 5.33 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `16410cdd28f9982c` |  |  |
| 2026-11-16T13:54:08+00:00 | mutation-changed-retry | 0 | 105.55 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `6d3584b92339a483` |  | gate=mutation score=0.935 threshold=0.8 killed=43 survived=3 files=1 base=origin/main |
| 2026-11-16T13:55:32+00:00 | regression-tests | 0 | 52.04 | `pytest -q` | `52a14281771b5849` |  |  |
| 2026-11-16T13:58:27+00:00 | no-js-fallback-red | 1 | 2.43 | `pytest -q tests/booking/interfaces/test_dialogs.py -k 'not_routed_table_offers or native_no_javascript'` | `7539cfb1b11cfca5` | assert response.status_code == 200 |  |
| 2026-11-16T14:00:28+00:00 | no-js-fallback | 0 | 5.73 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2d6b2c83d242f666` |  |  |
| 2026-11-16T14:01:27+00:00 | no-js-fallback | 0 | 6.36 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `70ca729620fcf127` |  |  |
| 2026-11-16T14:02:47+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T14:02:50+00:00 | build-django-check | 0 | 0.33 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T14:02:52+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T14:02:55+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-16T14:03:45+00:00 | behavior-tests | 0 | 47.71 | `pytest -q` | `0718abf27507a672` |  |  |
| 2026-11-16T14:04:36+00:00 | crap-coverage | 0 | 47.65 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `5305c65afe8dbb71` |  |  |
| 2026-11-16T14:04:39+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T14:04:41+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `e8a24bedc7973b35` |  | gate=crap max=26.0 threshold=30 over=0 methods=207 |
