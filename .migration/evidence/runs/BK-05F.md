# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T18:14:00+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:17:32+00:00 | tests-red | 2 | 6.71 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `e4c9bca63593996c` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-19T18:18:19+00:00 | tests-targeted | 0 | 3.51 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `3eae56deae2700cc` |  |  |
| 2026-11-19T18:18:46+00:00 | ui-checks | 0 | 0.4 | `python .migration/harness/tools/check_ui.py` | `ffb4265bfa237c5d` |  | gate=ui scope="templates changed since 5ec4a4b699c3194294e74243c50dea12b0e76163" templates=4 findings=0 |
| 2026-11-19T18:20:21+00:00 | tests-targeted | 0 | 3.91 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `6e6f3388206fe0be` |  |  |
| 2026-11-19T18:21:28+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:21:33+00:00 | build-django-check | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T18:22:24+00:00 | behavior | 0 | 48.04 | `pytest -q` | `dbcd9895af0e2d9f` |  |  |
| 2026-11-19T18:22:34+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:22:39+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `97f9e92869bb003f` |  |  |
| 2026-11-19T18:22:52+00:00 | tests-targeted | 0 | 3.65 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `3b1127cade8fe5e5` |  |  |
| 2026-11-19T18:23:14+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:23:17+00:00 | build-django-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T18:24:06+00:00 | behavior | 0 | 45.65 | `pytest -q` | `d68124051610b34c` |  |  |
| 2026-11-19T18:24:09+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:24:12+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T18:24:16+00:00 | idiom-layers | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T18:24:20+00:00 | idiom-ui | 0 | 0.42 | `python .migration/harness/tools/check_ui.py` | `ffb4265bfa237c5d` |  | gate=ui scope="templates changed since 5ec4a4b699c3194294e74243c50dea12b0e76163" templates=4 findings=0 |
| 2026-11-19T18:25:07+00:00 | crap-coverage | 0 | 44.08 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `17705e18b0e6d2da` |  |  |
| 2026-11-19T18:25:11+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:25:14+00:00 | crap-threshold | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `4bd0ec77941d6795` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-19T18:30:55+00:00 | mutation-changed | 1 | 337.06 | `python .migration/harness/tools/afs-mutation` | `e4b3619c7ec4cf5f` | afs-mutation: FAILED score=0.702 threshold=0.8 killed=40 survived=17 skipped=0 files=1 jobs=1 base=5ec4a4b699c3194294e74 | gate=mutation score=0.702 threshold=0.8 killed=40 survived=17 files=1 base=5ec4a4b699c3194294e74243c50dea12b0e76163 |
| 2026-11-19T18:32:26+00:00 | diagnostic-booking-tests | 0 | 11.13 | `pytest -q tests/booking` | `96e7375dbb090905` |  |  |
| 2026-11-19T18:33:05+00:00 | diagnostic-mutant-heading | 0 | 1.79 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_page_displays_cargo_details_and_candidate_itinerary_properties` | `1c6b0233fa8cd732` |  |  |
| 2026-11-19T18:34:04+00:00 | regression-guards | 1 | 5.29 | `python -m pytest -q tests/booking/interfaces/test_route_selection.py` | `97a332bedd61369f` | assert response.status_code == 200 |  |
| 2026-11-19T18:34:23+00:00 | regression-guards-green | 0 | 5.19 | `python -m pytest -q tests/booking/interfaces/test_route_selection.py` | `ed35e3e4882dd043` |  |  |
| 2026-11-19T18:34:35+00:00 | heading-assertion-mutant | 1 | 1.84 | `python -m pytest -q tests/booking/interfaces/test_route_selection.py::test_route_page_displays_cargo_details_and_candidate_itinerary_properties` | `4caa47b66018565e` | assert response.status_code == 200 |  |
| 2026-11-19T18:35:21+00:00 | regression-guards-final | 1 | 5.28 | `python -m pytest -q tests/booking/interfaces/test_route_selection.py` | `c466cbad677583d4` | E       KeyError: 0 |  |
| 2026-11-19T18:35:46+00:00 | regression-guards-final | 0 | 5.2 | `python -m pytest -q tests/booking/interfaces/test_route_selection.py` | `ed35e3e4882dd043` |  |  |
| 2026-11-19T18:36:13+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:36:20+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T18:36:23+00:00 | idiom-layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T18:36:26+00:00 | idiom-ui | 0 | 0.42 | `python .migration/harness/tools/check_ui.py` | `ffb4265bfa237c5d` |  | gate=ui scope="templates changed since 5ec4a4b699c3194294e74243c50dea12b0e76163" templates=4 findings=0 |
| 2026-11-19T18:40:47+00:00 | mutation-changed-final | 0 | 258.57 | `python .migration/harness/tools/afs-mutation` | `822020ed9045793a` |  | gate=mutation score=0.912 threshold=0.8 killed=52 survived=5 files=1 base=5ec4a4b699c3194294e74243c50dea12b0e76163 |
| 2026-11-19T18:41:31+00:00 | error-message-mutant-check | 0 | 1.87 | `python -m pytest -q tests/booking/interfaces/test_route_selection.py::test_invalid_candidate_selection_is_reported_without_assigning_a_route` | `7edfb975894be936` |  |  |
| 2026-11-19T18:41:58+00:00 | error-message-probe | 0 | 1.91 | `python -m pytest -q tests/booking/interfaces/test_route_selection.py::test_invalid_candidate_selection_is_reported_without_assigning_a_route` | `f7c9e83971975956` |  |  |
| 2026-11-19T18:42:11+00:00 | exact-alert-assertion-mutant | 1 | 1.92 | `python -m pytest -q tests/booking/interfaces/test_route_selection.py::test_invalid_candidate_selection_is_reported_without_assigning_a_route` | `73e11c15ae18b4e0` | assert response.status_code == 200 |  |
| 2026-11-19T18:42:28+00:00 | exact-alert-assertion-green | 0 | 5.18 | `python -m pytest -q tests/booking/interfaces/test_route_selection.py` | `946747511a49055a` |  |  |
| 2026-11-19T18:42:37+00:00 | cargo-context-mutant-check | 0 | 1.83 | `python -m pytest -q tests/booking/interfaces/test_route_selection.py::test_route_page_displays_cargo_details_and_candidate_itinerary_properties` | `6c677bdc128b19c8` |  |  |
| 2026-11-19T18:42:58+00:00 | cargo-details-assertion-mutant | 1 | 1.94 | `python -m pytest -q tests/booking/interfaces/test_route_selection.py::test_route_page_displays_cargo_details_and_candidate_itinerary_properties` | `3569177d9b6f90c9` | assert response.status_code == 200 |  |
| 2026-11-19T18:43:10+00:00 | route-tests-after-assertions | 0 | 5.29 | `python -m pytest -q tests/booking/interfaces/test_route_selection.py` | `b9b9d889f90e6b37` |  |  |
| 2026-11-19T18:47:46+00:00 | mutation-changed-final | 0 | 251.98 | `python .migration/harness/tools/afs-mutation` | `3faf2339147f42d6` |  | gate=mutation score=0.947 threshold=0.8 killed=54 survived=3 files=1 base=5ec4a4b699c3194294e74243c50dea12b0e76163 |
| 2026-11-19T18:47:55+00:00 | final-build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:47:59+00:00 | final-build-django-check | 0 | 0.28 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T18:48:47+00:00 | final-behavior | 0 | 45.86 | `pytest -q` | `174c32765c720f53` |  |  |
| 2026-11-19T18:48:49+00:00 | final-idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:48:52+00:00 | final-idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T18:48:54+00:00 | final-idiom-layers | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T18:48:58+00:00 | final-idiom-ui | 0 | 0.43 | `python .migration/harness/tools/check_ui.py` | `ffb4265bfa237c5d` |  | gate=ui scope="templates changed since 5ec4a4b699c3194294e74243c50dea12b0e76163" templates=4 findings=0 |
| 2026-11-19T18:49:46+00:00 | final-crap-coverage | 0 | 45.95 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `1130f8cdae277c3a` |  |  |
| 2026-11-19T18:49:50+00:00 | final-crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:49:53+00:00 | final-crap-threshold | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `f774058d945ff59b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
