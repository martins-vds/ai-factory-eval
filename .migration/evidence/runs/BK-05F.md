# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T12:32:58+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:36:00+00:00 | route-selection-red | 2 | 2.68 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `7afd4fc89a879bb2` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-18T12:36:36+00:00 | route-selection-tests | 1 | 3.99 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `815295e43bae075e` | assert route_response.status_code == 200 |  |
| 2026-11-18T12:36:48+00:00 | route-selection-tests | 0 | 3.8 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `0a12e90a870401ae` |  |  |
| 2026-11-18T12:37:39+00:00 | route-selection-tests | 0 | 4.29 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `523e69b47e13e49c` |  |  |
| 2026-11-18T12:39:14+00:00 | route-selection-tests | 0 | 4.7 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `87646c4ae6d185e9` |  |  |
| 2026-11-18T12:40:05+00:00 | build-compileall | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:40:10+00:00 | build-django-check | 0 | 0.34 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T12:40:13+00:00 | idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:40:16+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T12:40:20+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T12:40:24+00:00 | idiom-ui | 0 | 0.51 | `python .migration/harness/tools/check_ui.py` | `ae1a490ff1d87ff2` |  | gate=ui scope="templates changed since 55d5c2086c036dc31ed919483224aa9079f68f3b" templates=1 findings=0 |
| 2026-11-18T12:40:32+00:00 | behavior | 0 | 4.24 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `e4429539cf6c68d2` |  |  |
| 2026-11-18T12:41:52+00:00 | crap-coverage | 0 | 72.03 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `44bff54839239b05` |  |  |
| 2026-11-18T12:41:55+00:00 | crap-lizard | 0 | 0.16 | `lizard --csv src` | `b1ff73cfb53e5eea` | 16,3,86,6,16,"_origin_step@38-53@src/cargotracker/booking/interfaces/wizard/views.py","src/cargotracker/booking/interfac |  |
| 2026-11-18T12:41:58+00:00 | crap-report | 1 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `1f315dff0c7b9238` |  |  |
| 2026-11-18T12:42:05+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:42:09+00:00 | crap-report | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `5b51a1602fc10e58` |  | gate=crap max=26.0 threshold=30 over=0 methods=202 |
| 2026-11-18T12:45:47+00:00 | mutation-changed | 1 | 213.71 | `bash -c 'python .migration/harness/tools/afs-mutation --changed-since origin/main'` | `9b3ccdf0daf05cc1` | afs-mutation: FAILED score=0.655 threshold=0.8 killed=19 survived=10 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.655 threshold=0.8 killed=19 survived=10 files=1 base=origin/main |
| 2026-11-18T12:49:33+00:00 | route-selection-tests | 0 | 4.42 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `8952f2cbb4a11cd6` |  |  |
| 2026-11-18T12:49:51+00:00 | idiom-ruff-check | 1 | 0.01 | `ruff check` | `4424a0bf74e7c928` | Found 1 error. |  |
| 2026-11-18T12:50:09+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:50:12+00:00 | idiom-ruff-format | 1 | 0.01 | `ruff format --check` | `118b19806f85293c` |  |  |
| 2026-11-18T12:50:20+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T12:50:24+00:00 | idiom-layers | 0 | 0.15 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T12:50:28+00:00 | idiom-ui | 0 | 0.51 | `python .migration/harness/tools/check_ui.py` | `ae1a490ff1d87ff2` |  | gate=ui scope="templates changed since 55d5c2086c036dc31ed919483224aa9079f68f3b" templates=1 findings=0 |
| 2026-11-18T12:50:38+00:00 | behavior | 0 | 4.42 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `7906651f04bf7c9a` |  |  |
