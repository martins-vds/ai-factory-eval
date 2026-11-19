# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T21:38:57+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:42:35+00:00 | route-tests-red | 2 | 2.22 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `5b1981da916f2868` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-19T21:44:11+00:00 | route-tests-green-1 | 0 | 3.65 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `f59ca3387342dfc0` |  |  |
| 2026-11-19T21:44:52+00:00 | route-tests-green-2 | 0 | 4.49 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `36e16de7f4d22ddf` |  |  |
| 2026-11-19T21:45:08+00:00 | route-ruff-check | 0 | 0.01 | `ruff check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T21:45:10+00:00 | route-ruff-format | 1 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `f8044c57ecc8352c` | 143 \|     assert 'Itinerary' in details_response.content.decode() |  |
| 2026-11-19T21:45:15+00:00 | route-ruff-format-fix | 0 | 0.01 | `ruff format src/cargotracker/booking/interfaces/route_selection/views.py tests/booking/interfaces/test_route_selection.py` | `96a977f329ec3c59` |  |  |
| 2026-11-19T21:45:23+00:00 | route-tests-final-targeted | 0 | 4.48 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `1cb8558b250f917d` |  |  |
| 2026-11-19T21:45:26+00:00 | route-ui-check | 0 | 0.45 | `python .migration/harness/tools/check_ui.py` | `9cf1220ce5965a3f` |  | gate=ui scope="templates changed since 6d29ae7f70131c9eb6ea6964c5eacb3650352052" templates=3 findings=0 |
| 2026-11-19T21:48:08+00:00 | route-tests-green-3 | 0 | 4.56 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `8bf1065575ffd50b` |  |  |
| 2026-11-19T21:48:12+00:00 | route-layers-check | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T21:48:23+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:48:27+00:00 | build-check | 0 | 0.33 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T21:49:28+00:00 | behavior | 0 | 56.93 | `pytest -q` | `8d4aec4c7f5c1379` |  |  |
| 2026-11-19T21:49:31+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T21:49:34+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T21:49:39+00:00 | idiom-layers | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T21:49:42+00:00 | idiom-ui | 0 | 0.47 | `python .migration/harness/tools/check_ui.py` | `9cf1220ce5965a3f` |  | gate=ui scope="templates changed since 6d29ae7f70131c9eb6ea6964c5eacb3650352052" templates=3 findings=0 |
| 2026-11-19T21:50:43+00:00 | crap-coverage | 0 | 56.48 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `4ca6a19845508d3f` |  |  |
| 2026-11-19T21:50:46+00:00 | crap-lizard | 0 | 0.13 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:50:51+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `3ccc159daea5b778` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-19T21:56:58+00:00 | mutation-changed | 1 | 362.2 | `python .migration/harness/tools/afs-mutation` | `af90b5e5c10ca724` | afs-mutation: FAILED score=0.794 threshold=0.8 killed=50 survived=13 skipped=0 files=1 jobs=1 base=6d29ae7f70131c9eb6ea6 | gate=mutation score=0.794 threshold=0.8 killed=50 survived=13 files=1 base=6d29ae7f70131c9eb6ea6964c5eacb3650352052 |
| 2026-11-19T21:57:32+00:00 | route-tests-format | 0 | 0.01 | `ruff format tests/booking/interfaces/test_route_selection.py` | `d807f3580f2470a7` |  |  |
| 2026-11-19T21:57:41+00:00 | route-tests-green-4 | 0 | 4.82 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `38ca45009f5bcefb` |  |  |
| 2026-11-19T22:03:38+00:00 | mutation-changed-2 | 0 | 353.51 | `python .migration/harness/tools/afs-mutation` | `1ca17f42d6c2b700` |  | gate=mutation score=0.841 threshold=0.8 killed=53 survived=10 files=1 base=6d29ae7f70131c9eb6ea6964c5eacb3650352052 |
| 2026-11-19T22:04:15+00:00 | final-build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T22:04:20+00:00 | final-build-check | 0 | 0.34 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T22:05:22+00:00 | final-behavior | 0 | 57.36 | `pytest -q` | `bbe1644432fad770` |  |  |
| 2026-11-19T22:05:26+00:00 | final-idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T22:05:32+00:00 | final-idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T22:05:36+00:00 | final-idiom-layers | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T22:05:40+00:00 | final-idiom-ui | 0 | 0.46 | `python .migration/harness/tools/check_ui.py` | `9cf1220ce5965a3f` |  | gate=ui scope="templates changed since 6d29ae7f70131c9eb6ea6964c5eacb3650352052" templates=3 findings=0 |
| 2026-11-19T22:06:41+00:00 | final-crap-coverage | 0 | 56.33 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `73ad0c7f61fd9820` |  |  |
| 2026-11-19T22:06:45+00:00 | final-crap-lizard | 0 | 0.14 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T22:06:48+00:00 | final-crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `3ccc159daea5b778` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-19T22:08:10+00:00 | regression | 0 | 54.19 | `pytest -q` | `ac6e1c4d7cd57271` |  |  |
| 2026-11-19T22:13:50+00:00 | route-security-regression | 0 | 1.36 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_assignment_redirect_quotes_tracking_id` | `957a5010c70f683c` |  |  |
| 2026-11-19T22:13:52+00:00 | final-build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T22:13:54+00:00 | final-build-check | 0 | 0.34 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T22:13:56+00:00 | final-idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T22:13:58+00:00 | final-idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T22:14:01+00:00 | final-idiom-layers | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T22:14:04+00:00 | final-idiom-ui | 0 | 0.47 | `python .migration/harness/tools/check_ui.py` | `9cf1220ce5965a3f` |  | gate=ui scope="templates changed since 6d29ae7f70131c9eb6ea6964c5eacb3650352052" templates=3 findings=0 |
| 2026-11-19T22:15:03+00:00 | final-behavior | 0 | 55.69 | `pytest -q` | `1e9f9bed9b682132` |  |  |
| 2026-11-19T22:16:01+00:00 | final-crap-coverage | 0 | 55.15 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `01e3818ca9e0e90e` |  |  |
| 2026-11-19T22:16:04+00:00 | final-crap-lizard | 0 | 0.13 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T22:16:06+00:00 | final-crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `d479fc5a8ce74a96` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-19T22:22:14+00:00 | mutation-changed | 0 | 365.42 | `python .migration/harness/tools/afs-mutation` | `acac72edbdbb1a62` |  | gate=mutation score=0.828 threshold=0.8 killed=53 survived=11 files=1 base=6d29ae7f70131c9eb6ea6964c5eacb3650352052 |
| 2026-11-19T22:23:10+00:00 | regression | 0 | 54.43 | `pytest -q` | `f8e3eb4e8c86f5dd` |  |  |
| 2026-11-19T22:25:00+00:00 | route-security-regression | 1 | 1.46 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_assignment_redirect_quotes_tracking_id` | `a20d42f06e791c64` | # friendly in error messages. |  |
| 2026-11-19T22:25:12+00:00 | route-security-regression | 0 | 1.39 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_assignment_redirects_to_details_route` | `2082fa6110502427` |  |  |
| 2026-11-19T22:25:29+00:00 | route-tests-final-targeted | 0 | 4.95 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `be97629d9bfe259f` |  |  |
| 2026-11-19T22:25:32+00:00 | final-build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T22:25:35+00:00 | final-build-check | 0 | 0.34 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T22:25:37+00:00 | final-idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T22:25:40+00:00 | final-idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T22:25:43+00:00 | final-idiom-layers | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T22:25:47+00:00 | final-idiom-ui | 0 | 0.48 | `python .migration/harness/tools/check_ui.py` | `9cf1220ce5965a3f` |  | gate=ui scope="templates changed since 6d29ae7f70131c9eb6ea6964c5eacb3650352052" templates=3 findings=0 |
| 2026-11-19T22:26:43+00:00 | final-behavior | 0 | 53.83 | `pytest -q` | `0adfa016b5e7246f` |  |  |
| 2026-11-19T22:27:40+00:00 | final-crap-coverage | 0 | 54.7 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `cb221431ec551ab8` |  |  |
