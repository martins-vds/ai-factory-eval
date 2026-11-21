# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T02:42:10+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T02:43:15+00:00 | red-route-selection | 2 | 2.64 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `8ed49923e0692360` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-21T02:43:41+00:00 | green-route-selection | 1 | 2.3 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `3677bd7f8696f92e` | assert cargo is not None |  |
| 2026-11-21T02:43:50+00:00 | green-route-selection | 1 | 1.95 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `91f25a2300b213a0` | assert cargo is not None |  |
| 2026-11-21T02:43:59+00:00 | green-route-selection | 0 | 1.94 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `2123715683aceacd` |  |  |
| 2026-11-21T02:44:30+00:00 | route-selection-tests | 0 | 2.26 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `44cc03476d246aff` |  |  |
| 2026-11-21T02:44:38+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T02:44:38+00:00 | build | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T02:44:38+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `0d14f816d6d473f8` |  |  |
| 2026-11-21T02:44:38+00:00 | idiom-layers | 0 | 0.1 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T02:44:38+00:00 | build-check | 0 | 0.25 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T02:44:38+00:00 | idiom-ui | 0 | 0.35 | `python .migration/harness/tools/check_ui.py` | `65cd138b49f3db44` |  | gate=ui scope="templates changed since e2ecfc53f83d7ede9376c72b89117d8f03ac2f86" templates=2 findings=0 |
| 2026-11-21T02:44:42+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T02:45:41+00:00 | crap | 0 | 55.05 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `23556c2baf03a2ed` |  |  |
| 2026-11-21T02:45:42+00:00 | crap-lizard | 0 | 0.14 | `lizard --csv src` | `c0ea1dfe1c388d62` | 16,3,86,6,16,"_origin_step@38-53@src/cargotracker/booking/interfaces/wizard/views.py","src/cargotracker/booking/interfac |  |
| 2026-11-21T02:45:42+00:00 | crap-score | 1 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `1f315dff0c7b9238` |  |  |
| 2026-11-21T02:45:44+00:00 | mutation-changed | 1 | 57.62 | `python .migration/harness/tools/afs-mutation` | `0e27b5b502232ea3` | afs-mutation: FAILED score=0.571 threshold=0.8 killed=16 survived=12 skipped=0 files=1 jobs=1 base=e2ecfc53f83d7ede9376c | gate=mutation score=0.571 threshold=0.8 killed=16 survived=12 files=1 base=e2ecfc53f83d7ede9376c72b89117d8f03ac2f86 |
| 2026-11-21T02:46:01+00:00 | regression | 1 | 74.67 | `pytest -q` | `a2d36c4d10226b1f` | _ ERROR at setup of test_registration_persists_new_cargo_with_generated_id_and_empty_itinerary _ |  |
| 2026-11-21T02:46:18+00:00 | route-selection-tests | 0 | 3.36 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `07fbeb6f5f8ae964` |  |  |
| 2026-11-21T02:47:01+00:00 | regression | 0 | 39.47 | `pytest -q` | `ea7d34cf7fb52abf` |  |  |
| 2026-11-21T02:48:36+00:00 | mutation-changed | 1 | 134.8 | `python .migration/harness/tools/afs-mutation` | `935d2910bc4fbae2` | afs-mutation: FAILED score=0.714 threshold=0.8 killed=20 survived=8 skipped=0 files=1 jobs=1 base=e2ecfc53f83d7ede9376c7 | gate=mutation score=0.714 threshold=0.8 killed=20 survived=8 files=1 base=e2ecfc53f83d7ede9376c72b89117d8f03ac2f86 |
| 2026-11-21T02:49:04+00:00 | route-selection-tests | 0 | 3.88 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `45a97293789d26ff` |  |  |
| 2026-11-21T02:50:12+00:00 | mutation-changed | 0 | 65.03 | `python .migration/harness/tools/afs-mutation` | `933b187cd6c90042` |  | gate=mutation score=0.857 threshold=0.8 killed=24 survived=4 files=1 base=e2ecfc53f83d7ede9376c72b89117d8f03ac2f86 |
| 2026-11-21T02:50:27+00:00 | crap-lizard | 0 | 0.09 | `sh -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T02:50:27+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0cea1cdfeb73461b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-21T02:52:08+00:00 | route-selection-tests | 0 | 3.93 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `6952f4ed683bae13` |  |  |
| 2026-11-21T02:53:19+00:00 | mutation-changed | 0 | 66.91 | `python .migration/harness/tools/afs-mutation` | `dd0a022d86a8a2b0` |  | gate=mutation score=0.867 threshold=0.8 killed=26 survived=4 files=1 base=e2ecfc53f83d7ede9376c72b89117d8f03ac2f86 |
| 2026-11-21T02:55:01+00:00 | idiom-ruff | 1 | 0.01 | `ruff check` | `0cab0dcb295dd944` | Found 1 error. |  |
| 2026-11-21T02:55:01+00:00 | build | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T02:55:01+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T02:55:02+00:00 | idiom-layers | 0 | 0.1 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T02:55:02+00:00 | build-check | 0 | 0.32 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T02:55:02+00:00 | idiom-ui | 0 | 0.38 | `python .migration/harness/tools/check_ui.py` | `65cd138b49f3db44` |  | gate=ui scope="templates changed since e2ecfc53f83d7ede9376c72b89117d8f03ac2f86" templates=2 findings=0 |
| 2026-11-21T02:55:06+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T02:55:06+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T02:55:46+00:00 | crap | 0 | 36.21 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `10d9addaed6afe91` |  |  |
| 2026-11-21T02:55:46+00:00 | crap-lizard | 0 | 0.1 | `sh -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T02:55:46+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0cea1cdfeb73461b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-21T02:56:28+00:00 | regression | 0 | 35.75 | `pytest -q` | `387a556cafa46dcb` |  |  |
| 2026-11-21T02:57:31+00:00 | build | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T02:57:32+00:00 | build-check | 0 | 0.27 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T02:58:37+00:00 | mutation-changed | 0 | 65.46 | `python .migration/harness/tools/afs-mutation` | `dd0a022d86a8a2b0` |  | gate=mutation score=0.867 threshold=0.8 killed=26 survived=4 files=1 base=e2ecfc53f83d7ede9376c72b89117d8f03ac2f86 |
