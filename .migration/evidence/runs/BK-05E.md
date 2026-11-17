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
| 2026-11-17T19:20:30+00:00 | setup-probe | 0 | 0.01 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T19:22:21+00:00 | build-compileall | 0 | 0.11 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T19:22:26+00:00 | build-django-check | 0 | 1.67 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-17T19:22:29+00:00 | idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T19:22:32+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `b30e83bb722165b1` |  |  |
| 2026-11-17T19:22:35+00:00 | idiom-layers | 1 | 0.17 | `python .migration/harness/tools/check_layers.py` | `844177b805e7a5cb` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=1 known=3 |
| 2026-11-17T19:22:41+00:00 | idiom-ui | 1 | 0.48 | `python .migration/harness/tools/check_ui.py` | `ded165534558ef10` | templates/booking/wizard/_deadline_form.html:5: sends an htmx request ('hx-post'), but nothing handles error responses:  | gate=ui scope="templates changed since d1ee513dfb9fc8d33f066897c0a68788a77ec678" templates=10 findings=1 |
| 2026-11-17T19:24:04+00:00 | tests | 0 | 73.89 | `pytest -q` | `3605d1a2b18154db` |  |  |
| 2026-11-17T19:24:50+00:00 | tests-cargo-not-found-message | 1 | 2.68 | `pytest -q tests/booking/interfaces/test_cargo_details.py::test_unknown_and_stale_cargo_details_render_cargo_not_found_message` | `1508268b7885d9cf` | assert response.status_code == 404 |  |
| 2026-11-17T19:25:41+00:00 | tests-cargo-details | 1 | 4.05 | `pytest -q tests/booking/interfaces/test_cargo_details.py` | `3e8d03ec5f2a6bc1` | assert response.status_code == 404 |  |
| 2026-11-17T19:25:50+00:00 | build-compileall-final | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T19:25:54+00:00 | build-django-check-final | 0 | 0.39 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-17T19:25:57+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T19:26:01+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `b30e83bb722165b1` |  |  |
| 2026-11-17T19:26:05+00:00 | idiom-layers-final | 1 | 0.16 | `python .migration/harness/tools/check_layers.py` | `844177b805e7a5cb` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=1 known=3 |
| 2026-11-17T19:26:09+00:00 | idiom-ui-final | 1 | 0.47 | `python .migration/harness/tools/check_ui.py` | `ded165534558ef10` | templates/booking/wizard/_deadline_form.html:5: sends an htmx request ('hx-post'), but nothing handles error responses:  | gate=ui scope="templates changed since d1ee513dfb9fc8d33f066897c0a68788a77ec678" templates=10 findings=1 |
| 2026-11-17T19:27:20+00:00 | tests-final | 1 | 65.09 | `pytest -q` | `8e7f5a953a148587` | assert response.status_code == 404 |  |
| 2026-11-17T19:28:41+00:00 | crap-coverage-final | 1 | 61.96 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `b8a28bc81b118efa` | assert response.status_code == 404 |  |
| 2026-11-17T19:28:48+00:00 | crap-lizard-final | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T19:28:54+00:00 | crap-score-final | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `8cb946f24132ab4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=197 |
| 2026-11-17T19:29:32+00:00 | crap-top-method | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --top 1` | `1dbcc237fa0f375e` |  |  |
| 2026-11-17T19:39:15+00:00 | mutation-changed-final | 2 | 568.95 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `598d5a04098407f3` | afs-mutation: mutmut failed on src/cargotracker/booking/interfaces/dashboard/views.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=1 files=4 base=origin/main |
