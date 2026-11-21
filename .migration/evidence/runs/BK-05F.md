# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T20:32:51+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:35:56+00:00 | route-tests-red | 2 | 1.04 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `d90b7782fcb3b73d` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-21T20:37:08+00:00 | route-tests-green | 0 | 2.93 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `bd07ca1614724377` |  |  |
| 2026-11-21T20:38:18+00:00 | route-tests-green2 | 0 | 2.95 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `bd07ca1614724377` |  |  |
| 2026-11-21T20:39:44+00:00 | candidate-selection-red | 1 | 1.79 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_candidate_assignment_redirects_to_cargo_details_and_renders_assigned_itinerary` | `862b1cbe7db9c20d` | >       assert len(candidate_tokens) == 2 |  |
| 2026-11-21T20:40:07+00:00 | invalid-selection-red | 1 | 1.81 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_invalid_candidate_token_displays_error_without_requesting_new_candidates` | `57a8cd0091cd99a1` | assert response.status_code == 400 |  |
| 2026-11-21T20:40:34+00:00 | route-tests-green3 | 1 | 3.31 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `8b2597ae5b374b99` | >       assert len(candidate_tokens) == 2 |  |
| 2026-11-21T20:40:51+00:00 | route-tests-green4 | 0 | 3.36 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `c3b32caa90fa5633` |  |  |
| 2026-11-21T20:41:14+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `91e813e913baf00f` |  |  |
| 2026-11-21T20:41:14+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `a3de3ea4a7638e81` |  |  |
| 2026-11-21T20:41:14+00:00 | idiom-layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T20:41:15+00:00 | idiom-ui | 0 | 0.44 | `python .migration/harness/tools/check_ui.py` | `40d22036570507e9` |  | gate=ui scope="templates changed since 3e6a94a28aa0563b9ac475e7a4b4ef6821f8a516" templates=2 findings=0 |
| 2026-11-21T20:41:36+00:00 | route-tests-final | 0 | 3.32 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `9951aca7006aea4e` |  |  |
| 2026-11-21T20:42:01+00:00 | build-compileall | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:42:01+00:00 | build-django-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T20:42:01+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T20:42:01+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T20:42:01+00:00 | idiom-layers-final | 0 | 0.11 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T20:42:02+00:00 | idiom-ui-final | 0 | 0.44 | `python .migration/harness/tools/check_ui.py` | `40d22036570507e9` |  | gate=ui scope="templates changed since 3e6a94a28aa0563b9ac475e7a4b4ef6821f8a516" templates=2 findings=0 |
| 2026-11-21T20:42:51+00:00 | regression | 0 | 49.43 | `pytest -q` | `fd017a4b6c02b486` |  |  |
| 2026-11-21T20:43:46+00:00 | crap-coverage | 0 | 44.88 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `b723cdbb0845a869` |  |  |
| 2026-11-21T20:43:46+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:43:46+00:00 | crap-threshold | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `e227809556c58f4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=204 |
| 2026-11-21T20:48:02+00:00 | mutation-changed | 0 | 251.4 | `python .migration/harness/tools/afs-mutation` | `0743220cdd0995f4` |  | gate=mutation score=0.824 threshold=0.8 killed=42 survived=9 files=1 base=3e6a94a28aa0563b9ac475e7a4b4ef6821f8a516 |
| 2026-11-21T20:50:29+00:00 | screen-title-red | 1 | 1.84 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_select_itinerary_renders_candidates_when_routes_exist` | `4692c09347f53881` | assert response.status_code == 200 |  |
| 2026-11-21T20:50:42+00:00 | route-tests-final2 | 0 | 3.64 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `cd4366764674ec17` |  |  |
| 2026-11-21T20:50:56+00:00 | idiom-ruff-check-review-fix | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T20:50:56+00:00 | idiom-ruff-format-review-fix | 1 | 0.01 | `ruff format --check` | `cf9324e4133a92b2` | -     assert itinerary_one.index('CNHKG') < itinerary_one.index('NLRTM') < itinerary_one.index('AUMEL') |  |
| 2026-11-21T20:50:57+00:00 | idiom-ui-review-fix | 0 | 0.45 | `python .migration/harness/tools/check_ui.py` | `40d22036570507e9` |  | gate=ui scope="templates changed since 3e6a94a28aa0563b9ac475e7a4b4ef6821f8a516" templates=2 findings=0 |
| 2026-11-21T20:51:08+00:00 | idiom-format-review-fix-final | 0 | 0.01 | `ruff format --check tests/booking/interfaces/test_route_selection.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-21T20:51:12+00:00 | route-tests-final3 | 0 | 3.73 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `1c569b590fa8576c` |  |  |
| 2026-11-21T20:52:17+00:00 | build-compileall-review-final | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:52:17+00:00 | build-django-check-review-final | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T20:52:17+00:00 | idiom-ruff-check-review-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T20:52:17+00:00 | idiom-ruff-format-review-final | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T20:52:17+00:00 | idiom-layers-review-final | 0 | 0.11 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T20:52:18+00:00 | idiom-ui-review-final | 0 | 0.46 | `python .migration/harness/tools/check_ui.py` | `40d22036570507e9` |  | gate=ui scope="templates changed since 3e6a94a28aa0563b9ac475e7a4b4ef6821f8a516" templates=2 findings=0 |
| 2026-11-21T20:53:05+00:00 | regression-review-final | 0 | 47.71 | `pytest -q` | `5aab081136ec01d6` |  |  |
| 2026-11-21T20:53:53+00:00 | crap-coverage-review-final | 0 | 47.59 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `2dabfd133322b845` |  |  |
| 2026-11-21T20:53:53+00:00 | crap-lizard-review-final | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T20:53:53+00:00 | crap-threshold-review-final | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0cea1cdfeb73461b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-21T20:58:05+00:00 | mutation-changed-review-final | 0 | 252.14 | `python .migration/harness/tools/afs-mutation` | `c5e80dbedc2f5c69` |  | gate=mutation score=0.870 threshold=0.8 killed=47 survived=7 files=1 base=3e6a94a28aa0563b9ac475e7a4b4ef6821f8a516 |
