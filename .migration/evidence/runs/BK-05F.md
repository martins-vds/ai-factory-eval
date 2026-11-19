# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T13:55:17+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:59:45+00:00 | test-route-selection-red | 2 | 2.37 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `db51e39c18a4bcbb` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-19T14:00:48+00:00 | test-route-selection-green-1 | 1 | 3.43 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `23de5dd1727cb689` | assert response.status_code == 200 |  |
| 2026-11-19T14:01:17+00:00 | test-route-selection-diagnose | 1 | 3.2 | `pytest -q --showlocals tests/booking/interfaces/test_route_selection.py` | `392be886ba60917a` | assert response.status_code == 200 |  |
| 2026-11-19T14:01:41+00:00 | test-route-candidate-context | 1 | 1.85 | `pytest -q --showlocals tests/booking/interfaces/test_route_selection.py::test_route_page_displays_cargo_candidate_count_and_numbered_connected_legs` | `d0414460d486bf64` | assert response.status_code == 200 |  |
| 2026-11-19T14:02:16+00:00 | test-route-selection-green-2 | 0 | 3.28 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `90dfd6d8ae1500b9` |  |  |
| 2026-11-19T14:03:21+00:00 | test-route-selection-green-3 | 0 | 3.22 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `a3012a2f86fa8e15` |  |  |
| 2026-11-19T14:04:17+00:00 | test-route-selection-focused | 0 | 3.61 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `abd94044373779af` |  |  |
| 2026-11-19T14:06:25+00:00 | behavior | 0 | 3.8 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `00cf8eb30d42ecda` |  |  |
| 2026-11-19T14:06:28+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:06:33+00:00 | build-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T14:06:36+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T14:06:40+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T14:06:44+00:00 | idiom-layers | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T14:06:50+00:00 | idiom-ui | 0 | 0.41 | `python .migration/harness/tools/check_ui.py` | `edce9e2d569fd5ec` |  | gate=ui scope="templates changed since fba535a1ddd1ec6c8d349ce63200cddc661b4440" templates=1 findings=0 |
| 2026-11-19T14:07:40+00:00 | crap-coverage | 0 | 45.94 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `7d6b561e8f1a0256` |  |  |
| 2026-11-19T14:07:47+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:07:51+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `4877eadf5e45905d` |  | gate=crap max=26.0 threshold=30 over=0 methods=208 |
| 2026-11-19T14:08:39+00:00 | regression | 0 | 44.43 | `pytest -q` | `607555db017f6beb` |  |  |
| 2026-11-19T14:13:53+00:00 | mutation-changed | 1 | 306.64 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `72eb7ebff650e590` | afs-mutation: FAILED score=0.741 threshold=0.8 killed=43 survived=15 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.741 threshold=0.8 killed=43 survived=15 files=1 base=origin/main |
| 2026-11-19T14:14:33+00:00 | test-mutation-regressions | 0 | 3.84 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `18ad384061ea94dc` |  |  |
| 2026-11-19T14:19:56+00:00 | mutation-changed-final | 0 | 294.07 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `0ecf6ba8f1f5c928` |  | gate=mutation score=0.810 threshold=0.8 killed=47 survived=11 files=1 base=origin/main |
| 2026-11-19T14:21:28+00:00 | regression-final | 0 | 44.98 | `pytest -q` | `75a46d8b59ecd7d0` |  |  |
| 2026-11-19T14:21:32+00:00 | build-compile-final | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:21:36+00:00 | build-check-final | 0 | 0.33 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T14:21:40+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T14:21:44+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T14:21:49+00:00 | idiom-layers-final | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T14:21:53+00:00 | idiom-ui-final | 0 | 0.41 | `python .migration/harness/tools/check_ui.py` | `edce9e2d569fd5ec` |  | gate=ui scope="templates changed since fba535a1ddd1ec6c8d349ce63200cddc661b4440" templates=1 findings=0 |
| 2026-11-19T14:22:44+00:00 | crap-coverage-final | 0 | 45.86 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `25021e02b1683f58` |  |  |
| 2026-11-19T14:22:49+00:00 | crap-lizard-final | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:22:53+00:00 | crap-score-final | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `4877eadf5e45905d` |  | gate=crap max=26.0 threshold=30 over=0 methods=208 |
| 2026-11-19T14:25:55+00:00 | test-redirect-encoding | 0 | 3.58 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `d8a8cebc1af7bdb8` |  |  |
| 2026-11-19T14:27:33+00:00 | test-redirect-host-validation | 0 | 4.11 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `61a38df496171c3f` |  |  |
| 2026-11-19T14:28:42+00:00 | build-compile-codeqlfix | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:28:43+00:00 | build-check-codeqlfix | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T14:28:43+00:00 | idiom-ruff-check-codeqlfix | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T14:28:43+00:00 | idiom-ruff-format-codeqlfix | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T14:28:43+00:00 | idiom-layers-codeqlfix | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T14:28:43+00:00 | idiom-ui-codeqlfix | 0 | 0.42 | `python .migration/harness/tools/check_ui.py` | `edce9e2d569fd5ec` |  | gate=ui scope="templates changed since fba535a1ddd1ec6c8d349ce63200cddc661b4440" templates=1 findings=0 |
| 2026-11-19T14:28:52+00:00 | behavior-codeqlfix | 0 | 3.74 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `a999146e0e8feb8d` |  |  |
| 2026-11-19T14:29:38+00:00 | regression-codeqlfix | 0 | 46.02 | `pytest -q` | `38ec2a7076795af1` |  |  |
| 2026-11-19T14:30:29+00:00 | crap-coverage-codeqlfix | 0 | 44.59 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `e141e3bd8aa5bc87` |  |  |
| 2026-11-19T14:30:30+00:00 | crap-lizard-codeqlfix | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:30:30+00:00 | crap-score-codeqlfix | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `4877eadf5e45905d` |  | gate=crap max=26.0 threshold=30 over=0 methods=208 |
| 2026-11-19T14:35:51+00:00 | mutation-changed-codeqlfix | 1 | 318.18 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `7da930109e93da70` | afs-mutation: FAILED score=0.794 threshold=0.8 killed=50 survived=13 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.794 threshold=0.8 killed=50 survived=13 files=1 base=origin/main |
| 2026-11-19T14:36:24+00:00 | test-encoded-tracking-id | 0 | 2.03 | `pytest -q tests/booking/interfaces/test_route_selection.py::test_route_assignment_encodes_tracking_id_in_details_redirect` | `7eb11104642b7dc0` |  |  |
| 2026-11-19T14:42:18+00:00 | mutation-changed-encoded-id | 1 | 327.76 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `7da930109e93da70` | afs-mutation: FAILED score=0.794 threshold=0.8 killed=50 survived=13 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.794 threshold=0.8 killed=50 survived=13 files=1 base=origin/main |
