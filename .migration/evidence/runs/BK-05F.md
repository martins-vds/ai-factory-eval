# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T13:47:33+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:51:33+00:00 | route-selection-red | 2 | 4.14 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `ab4a2ff3557c30c7` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-19T13:52:28+00:00 | route-selection-green | 1 | 2.74 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `c55ab1c5b2e7c66a` | assert response.status_code == 200 |  |
| 2026-11-19T13:52:44+00:00 | route-selection-focused | 0 | 2.57 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `9c904c5062f49259` |  |  |
| 2026-11-19T13:54:29+00:00 | route-selection-security | 0 | 3.29 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `c34cb970c81748da` |  |  |
| 2026-11-19T13:55:28+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:55:28+00:00 | build-django-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T13:55:28+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T13:55:28+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `87c89a444ab87729` |  |  |
| 2026-11-19T13:55:46+00:00 | idiom-format-rerun | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T13:55:46+00:00 | idiom-layers | 1 | 0.13 | `python .migration/harness/tools/check_layers.py` | `1ad654ba857193d5` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=2 known=3 |
| 2026-11-19T13:56:19+00:00 | idiom-layers-rerun | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T13:56:22+00:00 | route-selection-layered | 0 | 2.97 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `d4b46ee8cad5ac5c` |  |  |
| 2026-11-19T13:56:34+00:00 | build-compile-rerun | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:56:34+00:00 | build-django-check-rerun | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T13:56:34+00:00 | idiom-ruff-check-rerun | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T13:56:34+00:00 | idiom-format-final | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T13:56:35+00:00 | idiom-ui | 0 | 0.41 | `python .migration/harness/tools/check_ui.py` | `eaa23ed8d6507eea` |  | gate=ui scope="templates changed since 4c8a19912b402ded1c63b287cf38e9dfc3763fd4" templates=1 findings=0 |
| 2026-11-19T13:57:31+00:00 | regression | 0 | 48.32 | `pytest -q` | `102ed2e7a5929ec1` |  |  |
| 2026-11-19T13:58:25+00:00 | crap-coverage | 0 | 44.85 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `0bc483b6635b89b6` |  |  |
| 2026-11-19T13:58:25+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:58:26+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `e227809556c58f4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=204 |
| 2026-11-19T14:02:26+00:00 | mutation-changed | 0 | 216.6 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `d43f64782e9d20a3` |  | gate=mutation score=0.878 threshold=0.8 killed=43 survived=6 files=1 base=origin/main |
| 2026-11-19T14:04:16+00:00 | route-token-binding | 0 | 3.35 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `f329478ba065a40c` |  |  |
| 2026-11-19T14:04:16+00:00 | format-check-token-binding | 1 | 0.01 | `ruff format --check` | `0067efcbbb68f3d4` |  |  |
| 2026-11-19T14:04:23+00:00 | format-check-token-binding-rerun | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T14:06:14+00:00 | regression-final | 0 | 46.9 | `pytest -q` | `90949bdfa8e58496` |  |  |
| 2026-11-19T14:09:47+00:00 | mutation-changed-final | 0 | 207.03 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `24854fa7664323d3` |  | gate=mutation score=0.898 threshold=0.8 killed=44 survived=5 files=1 base=origin/main |
