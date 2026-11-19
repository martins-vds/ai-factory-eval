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
