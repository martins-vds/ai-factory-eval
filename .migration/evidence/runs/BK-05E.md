# Run journal: BK-05E

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T18:23:06+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T18:27:09+00:00 | tests-red | 2 | 2.95 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_cargo_details.py` | `5919781dca1433e6` | _________ ERROR collecting tests/booking/interfaces/test_dashboard.py __________ |  |
| 2026-11-07T18:28:12+00:00 | tests-targeted | 0 | 2.94 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_cargo_details.py` | `d45996ff8b3a07ca` |  |  |
| 2026-11-07T18:28:43+00:00 | tests-targeted | 0 | 2.84 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_cargo_details.py` | `bf97953a21a0c167` |  |  |
| 2026-11-07T18:29:05+00:00 | build-compileall | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T18:29:05+00:00 | build-django-check | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-07T18:29:08+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-07T18:29:08+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `f7623b4d5336db55` | 77 \|     assert response.status_code == 200 |  |
| 2026-11-07T18:29:13+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `c7a0bcb17dd5241a` |  |  |
| 2026-11-07T18:30:01+00:00 | tests | 0 | 44.68 | `pytest -q` | `fde32fcce61583e5` |  |  |
| 2026-11-07T18:30:44+00:00 | crap-coverage | 0 | 37.61 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `ff6e6eba749aaa31` |  |  |
| 2026-11-07T18:30:44+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T18:30:44+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `efcf0c40f9c44d17` |  | gate=crap max=26.0 threshold=30 over=0 methods=180 |
| 2026-11-07T18:31:15+00:00 | mutation-changed | 0 | 25.98 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `4e8520baafe17cc5` |  | gate=mutation score=0.929 threshold=0.8 killed=13 survived=1 files=1 base=origin/main |
| 2026-11-17T05:01:54+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T05:04:08+00:00 | tests-detail-states | 1 | 5.08 | `pytest -q tests/booking/interfaces/test_cargo_details.py` | `51af06c81e2cf880` | E       NameError: name 'TrackingId' is not defined |  |
| 2026-11-17T05:04:18+00:00 | tests-detail-states | 0 | 2.73 | `pytest -q tests/booking/interfaces/test_cargo_details.py` | `5cc230b3cce8abef` |  |  |
| 2026-11-17T05:04:49+00:00 | build-compileall | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T05:04:50+00:00 | build-django-check | 0 | 0.28 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-17T05:04:53+00:00 | behavior | 0 | 3.48 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_cargo_details.py` | `42e23bc87b8c5ca7` |  |  |
| 2026-11-17T05:04:53+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `250efb9156a503a7` | Found 1 error. |  |
| 2026-11-17T05:05:10+00:00 | build-compileall | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T05:05:10+00:00 | build-django-check | 0 | 0.28 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-17T05:05:14+00:00 | behavior | 0 | 3.39 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_cargo_details.py` | `6765139c514dcd59` |  |  |
| 2026-11-17T05:05:14+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T05:05:14+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `b30e83bb722165b1` |  |  |
| 2026-11-17T05:05:14+00:00 | idiom-layers | 1 | 0.12 | `python .migration/harness/tools/check_layers.py` | `844177b805e7a5cb` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=1 known=3 |
| 2026-11-17T05:06:07+00:00 | regression | 0 | 44.5 | `pytest -q` | `65789f302e73f79c` |  |  |
| 2026-11-17T05:06:50+00:00 | crap-coverage | 0 | 42.5 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `295ddef40915d9fe` |  |  |
| 2026-11-17T05:06:50+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T05:06:50+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `8cb946f24132ab4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=197 |
| 2026-11-17T05:14:02+00:00 | mutation-changed | 0 | 432.56 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `99c3c637fc12de56` |  | gate=mutation score=0.919 threshold=0.8 killed=248 survived=22 files=4 base=origin/main |
| 2026-11-17T05:15:46+00:00 | behavior-notfound-message | 1 | 1.97 | `pytest -q tests/booking/interfaces/test_cargo_details.py::test_unknown_and_stale_cargo_details_return_http_404` | `707ed67d83b7ec6c` | assert unknown_response.status_code == 404 |  |
| 2026-11-17T05:16:25+00:00 | behavior-notfound-message | 1 | 2.49 | `pytest -q tests/booking/interfaces/test_cargo_details.py::test_unknown_and_stale_cargo_details_show_not_found_message` | `0fea5d99f9f7098b` | assert response.status_code == 404 |  |
| 2026-11-17T05:16:51+00:00 | behavior | 1 | 4.89 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/interfaces/test_cargo_details.py` | `4b3009b464f9e000` | assert response.status_code == 404 |  |
| 2026-11-17T05:17:34+00:00 | regression | 1 | 43.48 | `pytest -q` | `486634f20a6056b9` | assert response.status_code == 404 |  |
| 2026-11-17T05:17:34+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T05:17:35+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `b30e83bb722165b1` |  |  |
