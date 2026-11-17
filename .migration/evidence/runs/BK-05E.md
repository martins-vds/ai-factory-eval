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
| 2026-11-17T16:43:52+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T16:46:06+00:00 | build-compileall | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T16:46:06+00:00 | build-django-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-17T16:46:06+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T16:46:06+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `b30e83bb722165b1` |  |  |
| 2026-11-17T16:46:06+00:00 | idiom-layers | 1 | 0.08 | `python .migration/harness/tools/check_layers.py` | `844177b805e7a5cb` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=1 known=3 |
| 2026-11-17T16:46:07+00:00 | idiom-ui | 1 | 0.23 | `python .migration/harness/tools/check_ui.py` | `9c3e8a5707209c90` | templates/booking/wizard/_deadline_form.html:5: sends an htmx request ('hx-post'), but nothing handles error responses:  | gate=ui scope="templates changed since 580b559cd92a19aa2d5c891fe66dd5e162817e9b" templates=10 findings=1 |
| 2026-11-17T16:46:39+00:00 | behavior | 0 | 32.39 | `pytest -q` | `799dd0b0bd447f64` |  |  |
| 2026-11-17T16:47:11+00:00 | crap-coverage | 0 | 31.25 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `fbb16afaebd0a616` |  |  |
| 2026-11-17T16:47:11+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T16:47:11+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `8cb946f24132ab4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=197 |
| 2026-11-17T16:52:39+00:00 | mutation-changed | 0 | 327.97 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `99c3c637fc12de56` |  | gate=mutation score=0.919 threshold=0.8 killed=248 survived=22 files=4 base=origin/main |
| 2026-11-17T16:54:13+00:00 | tests-details | 0 | 1.98 | `pytest -q tests/booking/interfaces/test_cargo_details.py` | `f4bcd235d33b5e16` |  |  |
| 2026-11-17T16:54:13+00:00 | idiom-test-check | 0 | 0.01 | `ruff check tests/booking/interfaces/test_cargo_details.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T16:54:13+00:00 | idiom-test-format | 0 | 0.01 | `ruff format --check tests/booking/interfaces/test_cargo_details.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-17T16:56:23+00:00 | behavior-final | 0 | 33.6 | `pytest -q` | `e1ac81a019c2e3dd` |  |  |
| 2026-11-17T16:57:01+00:00 | crap-coverage-final | 0 | 37.57 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `baf6cdde6b835bbb` |  |  |
| 2026-11-17T16:57:01+00:00 | crap-lizard-final | 0 | 0.08 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T16:57:01+00:00 | crap-score-final | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `8cb946f24132ab4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=197 |
| 2026-11-17T16:57:01+00:00 | idiom-test-check-final | 0 | 0.01 | `ruff check tests/booking/interfaces/test_cargo_details.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T16:57:01+00:00 | idiom-test-format-final | 0 | 0.01 | `ruff format --check tests/booking/interfaces/test_cargo_details.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-17T17:02:24+00:00 | mutation-changed-final | 0 | 322.29 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `99c3c637fc12de56` |  | gate=mutation score=0.919 threshold=0.8 killed=248 survived=22 files=4 base=origin/main |
