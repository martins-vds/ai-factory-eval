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
| 2026-11-21T20:33:06+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:35:28+00:00 | build-compileall | 0 | 0.08 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:35:29+00:00 | build-django-check | 0 | 1.07 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T20:35:32+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T20:35:32+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `b30e83bb722165b1` |  |  |
| 2026-11-21T20:35:32+00:00 | idiom-layers | 1 | 0.13 | `python .migration/harness/tools/check_layers.py` | `844177b805e7a5cb` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=1 known=3 |
| 2026-11-21T20:35:44+00:00 | idiom-ui | 1 | 0.53 | `python .migration/harness/tools/check_ui.py` | `503b4034434af33b` | templates/booking/wizard/_deadline_form.html:5: sends an htmx request ('hx-post'), but nothing handles error responses:  | gate=ui scope="templates changed since 664dfb183f365f5519eaa07e381c1ea2370c3e5f" templates=10 findings=1 |
| 2026-11-21T20:37:01+00:00 | behavior | 0 | 64.41 | `pytest -q` | `cf18ff8acba83be0` |  |  |
| 2026-11-21T20:38:01+00:00 | regression | 0 | 57.0 | `pytest -q` | `e0aa751cfeb9c91e` |  |  |
| 2026-11-21T20:38:56+00:00 | crap-coverage | 0 | 51.74 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `bbb8d646e4b83514` |  |  |
| 2026-11-21T20:38:56+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:38:56+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `8cb946f24132ab4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=197 |
| 2026-11-21T20:39:37+00:00 | verifier-detail-branches | 0 | 3.27 | `pytest -q tests/booking/interfaces/test_cargo_details.py` | `f2c544c93476f701` |  |  |
| 2026-11-21T20:40:17+00:00 | final-build-compileall | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:40:17+00:00 | final-build-django-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T20:40:17+00:00 | final-idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T20:40:18+00:00 | final-idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `b30e83bb722165b1` |  |  |
| 2026-11-21T20:40:18+00:00 | final-idiom-layers | 1 | 0.13 | `python .migration/harness/tools/check_layers.py` | `844177b805e7a5cb` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=1 known=3 |
| 2026-11-21T20:40:25+00:00 | final-idiom-ui | 1 | 0.53 | `python .migration/harness/tools/check_ui.py` | `503b4034434af33b` | templates/booking/wizard/_deadline_form.html:5: sends an htmx request ('hx-post'), but nothing handles error responses:  | gate=ui scope="templates changed since 664dfb183f365f5519eaa07e381c1ea2370c3e5f" templates=10 findings=1 |
| 2026-11-21T20:41:19+00:00 | final-behavior | 0 | 52.09 | `pytest -q` | `fa66837d1633b1d3` |  |  |
| 2026-11-21T20:42:10+00:00 | final-regression | 0 | 50.83 | `pytest -q` | `ff7bbbf09f688c75` |  |  |
| 2026-11-21T20:43:05+00:00 | final-crap-coverage | 0 | 51.39 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `9de4bf17f3312dc7` |  |  |
| 2026-11-21T20:43:06+00:00 | final-crap-lizard | 0 | 0.13 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:43:06+00:00 | final-crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `8cb946f24132ab4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=197 |
| 2026-11-21T20:51:46+00:00 | final-mutation-changed | 0 | 518.4 | `python .migration/harness/tools/afs-mutation` | `965377e6a35d2b30` |  | gate=mutation score=0.919 threshold=0.8 killed=248 survived=22 files=4 base=664dfb183f365f5519eaa07e381c1ea2370c3e5f |
| 2026-11-21T20:56:01+00:00 | build-compileall | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:56:01+00:00 | build-django-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T20:56:01+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T20:56:01+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `b30e83bb722165b1` |  |  |
| 2026-11-21T20:56:01+00:00 | idiom-layers | 1 | 0.13 | `python .migration/harness/tools/check_layers.py` | `844177b805e7a5cb` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=1 known=3 |
| 2026-11-21T20:56:02+00:00 | idiom-ui | 1 | 0.52 | `python .migration/harness/tools/check_ui.py` | `503b4034434af33b` | templates/booking/wizard/_deadline_form.html:5: sends an htmx request ('hx-post'), but nothing handles error responses:  | gate=ui scope="templates changed since 664dfb183f365f5519eaa07e381c1ea2370c3e5f" templates=10 findings=1 |
| 2026-11-21T20:56:59+00:00 | behavior | 0 | 52.63 | `pytest -q` | `ab78179db160da5a` |  |  |
| 2026-11-21T20:57:51+00:00 | regression | 0 | 51.18 | `pytest -q` | `fe32ea1801fadc45` |  |  |
| 2026-11-21T20:58:44+00:00 | crap-coverage | 0 | 53.02 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `8d9ae713f72824f0` |  |  |
| 2026-11-21T20:58:44+00:00 | crap-lizard | 0 | 0.13 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:58:44+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `8cb946f24132ab4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=197 |
| 2026-11-21T21:07:24+00:00 | mutation-changed | 0 | 515.81 | `python .migration/harness/tools/afs-mutation` | `965377e6a35d2b30` |  | gate=mutation score=0.919 threshold=0.8 killed=248 survived=22 files=4 base=664dfb183f365f5519eaa07e381c1ea2370c3e5f |
