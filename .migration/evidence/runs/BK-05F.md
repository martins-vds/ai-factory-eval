# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T18:17:18+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:17:41+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:20:30+00:00 | tests-red | 2 | 2.31 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `f9ae0c1b351b3230` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-19T18:21:54+00:00 | tests-targeted | 1 | 1.45 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `cb12ebf8759e0dc0` | assert response.status_code == 200 |  |
| 2026-11-19T18:22:12+00:00 | tests-targeted | 0 | 1.32 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `2ec7ef7d45b9aad9` |  |  |
| 2026-11-19T18:22:51+00:00 | tests-targeted | 0 | 1.33 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `7fff5cb703d8bcd2` |  |  |
| 2026-11-19T18:23:25+00:00 | build-compile | 0 | 0.09 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:23:28+00:00 | build-check | 0 | 0.25 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T18:23:31+00:00 | idiom-ruff | 1 | 0.02 | `ruff check` | `c0747596e5526f68` | Found 1 error. |  |
| 2026-11-19T18:23:40+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:23:43+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T18:23:46+00:00 | idiom-layers | 0 | 0.09 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T18:23:49+00:00 | idiom-ui | 0 | 0.31 | `python .migration/harness/tools/check_ui.py` | `c6928b9bf593b828` |  | gate=ui scope="templates changed since 8e683c5e2b82c5f52930c14332316a662734c1e8" templates=1 findings=0 |
| 2026-11-19T18:24:29+00:00 | tests | 0 | 34.33 | `pytest -q` | `048bc6ceeff23a5a` |  |  |
| 2026-11-19T18:25:06+00:00 | crap-coverage | 0 | 32.39 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `bd2ec43a934e8100` |  |  |
| 2026-11-19T18:25:10+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:25:12+00:00 | crap-report | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `e227809556c58f4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=204 |
| 2026-11-19T18:27:53+00:00 | mutation-changed | 0 | 157.61 | `python .migration/harness/tools/afs-mutation` | `0fc82fd9eab7b008` |  | gate=mutation score=0.816 threshold=0.8 killed=40 survived=9 files=1 base=8e683c5e2b82c5f52930c14332316a662734c1e8 |
| 2026-11-19T18:28:43+00:00 | tests-targeted | 0 | 1.51 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `766e18661cfad437` |  |  |
| 2026-11-19T18:31:14+00:00 | mutation-changed | 0 | 146.61 | `python .migration/harness/tools/afs-mutation` | `2e46950440cd5ad5` |  | gate=mutation score=0.898 threshold=0.8 killed=44 survived=5 files=1 base=8e683c5e2b82c5f52930c14332316a662734c1e8 |
| 2026-11-19T18:33:18+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:33:21+00:00 | build-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T18:33:25+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:33:29+00:00 | idiom-format | 1 | 0.01 | `ruff format --check` | `6b4e922d749fb920` |  |  |
| 2026-11-19T18:33:38+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T18:33:42+00:00 | idiom-layers | 0 | 0.09 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T18:33:46+00:00 | idiom-ui | 0 | 0.32 | `python .migration/harness/tools/check_ui.py` | `c6928b9bf593b828` |  | gate=ui scope="templates changed since 8e683c5e2b82c5f52930c14332316a662734c1e8" templates=1 findings=0 |
| 2026-11-19T18:34:21+00:00 | tests | 0 | 31.18 | `pytest -q` | `dadeb63d1d458868` |  |  |
| 2026-11-19T18:34:57+00:00 | crap-coverage | 0 | 33.53 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `94928af3e22c2ac7` |  |  |
| 2026-11-19T18:34:59+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:35:02+00:00 | crap-report | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `e227809556c58f4e` |  | gate=crap max=26.0 threshold=30 over=0 methods=204 |
| 2026-11-19T18:35:26+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:37:09+00:00 | tests-targeted | 0 | 1.37 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `d7c74fd6e1de597d` |  |  |
| 2026-11-19T18:38:37+00:00 | tests-targeted | 0 | 1.38 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `05053cf90c259d51` |  |  |
