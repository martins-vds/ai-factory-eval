# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:45:43+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:51:09+00:00 | behavior-red | 1 | 4.49 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `5fa15ba8125c6b37` | assert response.status_code == 200 |  |
| 2026-11-18T03:51:24+00:00 | behavior-table-actions | 1 | 2.3 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `e3063ff31003e6c2` | assert response.status_code == 200 |  |
| 2026-11-18T03:51:36+00:00 | behavior-table-actions | 0 | 2.3 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `9a777c8cb819b44d` |  |  |
| 2026-11-18T03:52:55+00:00 | behavior-destination-red | 2 | 1.01 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `61bef741f07540ef` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T03:53:54+00:00 | behavior-destination | 0 | 2.79 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `fcd5f4644057ac59` |  |  |
| 2026-11-18T03:54:45+00:00 | behavior-destination-updates | 0 | 4.74 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `3043b238ba5b8844` |  |  |
| 2026-11-18T03:55:09+00:00 | behavior-deadline-red | 2 | 0.99 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `41619cd1318dffb5` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T03:55:34+00:00 | behavior-deadline-initial | 0 | 5.03 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `7e8e945dbb6219c8` |  |  |
| 2026-11-18T03:55:59+00:00 | behavior-dialogs | 0 | 8.01 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `e7c1a0070ecbccc0` |  |  |
| 2026-11-18T03:56:30+00:00 | behavior-dialogs-final | 0 | 8.97 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `90dfd59e3d9fb9c5` |  |  |
| 2026-11-18T03:56:36+00:00 | behavior-dashboard-regression | 0 | 2.95 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `67aae16ad4ff2d2c` |  |  |
| 2026-11-18T03:58:12+00:00 | behavior-dialogs-final | 0 | 8.88 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `9f517c6534fa8ebc` |  |  |
| 2026-11-18T03:58:18+00:00 | behavior-dashboard-regression | 0 | 2.83 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `9394ef6123ea1f3c` |  |  |
| 2026-11-18T03:58:31+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:58:37+00:00 | build-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T03:58:40+00:00 | idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T03:58:44+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `a9ac37a3f51c960d` | 104 \|     assert 'HX-Redirect' not in response |  |
| 2026-11-18T03:58:52+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-18T03:58:56+00:00 | idiom-layers | 0 | 0.18 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T03:58:59+00:00 | idiom-ui | 1 | 0.5 | `python .migration/harness/tools/check_ui.py` | `23e021ebb8229a1d` | templates/booking/dashboard/not_routed_table.html:35: sends an htmx request ('hx-get'), but nothing handles error respon | gate=ui scope="templates changed since b48a8ddc1d07a13c5e0259d739c638666327226b" templates=3 findings=3 |
| 2026-11-18T03:59:50+00:00 | behavior-dialog-errors-red | 1 | 2.93 | `pytest -q tests/booking/interfaces/test_dialogs.py -k not_found` | `f66f53b4f3f98d14` | assert response.status_code == 404 |  |
| 2026-11-18T04:00:20+00:00 | behavior-dialogs-final | 0 | 8.84 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `bf38e8cd47c004f5` |  |  |
| 2026-11-18T04:00:24+00:00 | idiom-ui | 0 | 0.51 | `python .migration/harness/tools/check_ui.py` | `0b96b646f2a107e0` |  | gate=ui scope="templates changed since b48a8ddc1d07a13c5e0259d739c638666327226b" templates=4 findings=0 |
| 2026-11-18T04:00:40+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T04:00:44+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-18T04:00:48+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T04:04:39+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T04:04:43+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T04:06:07+00:00 | behavior | 0 | 79.24 | `pytest -q` | `a1e22ef124694b2a` |  |  |
| 2026-11-18T04:06:16+00:00 | lint | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T04:06:18+00:00 | format | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-18T04:06:20+00:00 | layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T04:06:23+00:00 | ui | 0 | 0.52 | `python .migration/harness/tools/check_ui.py` | `0b96b646f2a107e0` |  | gate=ui scope="templates changed since b48a8ddc1d07a13c5e0259d739c638666327226b" templates=4 findings=0 |
| 2026-11-18T04:07:33+00:00 | crap-coverage | 0 | 66.02 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `050be942d73d519c` |  |  |
| 2026-11-18T04:07:35+00:00 | crap-complexity | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T04:07:38+00:00 | crap-score | 0 | 0.05 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `b766bed1c3025431` |  | gate=crap max=26.0 threshold=30 over=0 methods=207 |
| 2026-11-18T04:15:31+00:00 | mutation-changed | 1 | 470.08 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `d84de35198d005d7` | afs-mutation: FAILED score=0.776 threshold=0.8 killed=45 survived=13 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.776 threshold=0.8 killed=45 survived=13 files=1 base=origin/main |
| 2026-11-18T04:16:46+00:00 | mutation-focused-tests | 0 | 11.68 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0056a3303fd5cca3` |  |  |
| 2026-11-18T04:23:47+00:00 | mutation-changed | 0 | 414.62 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `fd1f0825d73eba9c` |  | gate=mutation score=0.948 threshold=0.8 killed=55 survived=3 files=1 base=origin/main |
