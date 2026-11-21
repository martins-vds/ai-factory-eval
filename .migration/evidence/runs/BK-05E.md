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
| 2026-11-21T18:52:49+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T18:55:36+00:00 | build-compileall | 0 | 0.1 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T18:55:38+00:00 | build-django-check | 0 | 1.53 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T18:55:38+00:00 | idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T18:55:38+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `b30e83bb722165b1` |  |  |
| 2026-11-21T18:55:38+00:00 | idiom-layers | 1 | 0.16 | `python .migration/harness/tools/check_layers.py` | `844177b805e7a5cb` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=1 known=3 |
| 2026-11-21T18:55:39+00:00 | idiom-ui | 1 | 0.66 | `python .migration/harness/tools/check_ui.py` | `148f8f9a77498de5` | templates/booking/wizard/_deadline_form.html:5: sends an htmx request ('hx-post'), but nothing handles error responses:  | gate=ui scope="templates changed since 10172ab14a07908784ae8f968b86953b2ddbb798" templates=10 findings=1 |
| 2026-11-21T18:56:44+00:00 | behavior | 0 | 64.6 | `pytest -q` | `6fe89aa37f398e9c` |  |  |
| 2026-11-21T18:57:43+00:00 | crap-coverage | 0 | 59.75 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `68b8afaf108871fa` |  |  |
| 2026-11-21T18:57:44+00:00 | crap-lizard | 0 | 0.18 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T18:57:44+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `8cb946f24132ab4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=197 |
| 2026-11-21T19:07:22+00:00 | mutation-changed | 0 | 578.28 | `python .migration/harness/tools/afs-mutation` | `2917779f4aea3706` |  | gate=mutation score=0.919 threshold=0.8 killed=248 survived=22 files=4 base=10172ab14a07908784ae8f968b86953b2ddbb798 |
| 2026-11-21T19:07:41+00:00 | cargo-details-contract | 1 | 7.59 | `pytest -q tests/booking/interfaces/test_cargo_details.py` | `0e0b7bbac9d2a978` | ____ ERROR at setup of test_cargo_details_render_route_fields_and_itinerary ____ |  |
| 2026-11-21T19:08:20+00:00 | regression | 0 | 57.74 | `pytest -q` | `9ed4d7c61a612c85` |  |  |
| 2026-11-21T19:08:35+00:00 | cargo-details-contract-retry | 1 | 3.83 | `pytest -q tests/booking/interfaces/test_cargo_details.py` | `0659bc0943843213` | assert unknown_response.status_code == 404 |  |
| 2026-11-21T19:09:43+00:00 | idiom-ruff-check-after-tests | 0 | 0.01 | `ruff check tests/booking/interfaces/test_cargo_details.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T19:09:43+00:00 | idiom-ruff-format-after-tests | 0 | 0.01 | `ruff format --check tests/booking/interfaces/test_cargo_details.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-21T19:11:21+00:00 | behavior-after-evidence | 1 | 72.91 | `pytest -q` | `554139d83c66ff60` | assert unknown_response.status_code == 404 |  |
| 2026-11-21T19:12:36+00:00 | regression-after-evidence | 1 | 75.06 | `pytest -q` | `46912d09da84de34` | assert unknown_response.status_code == 404 |  |
