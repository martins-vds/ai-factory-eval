# Run journal: BK-05K

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T22:04:44+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T22:08:35+00:00 | red | 1 | 5.02 | `pytest -q tests/test_htmx_errors.py` | `24b0bae78b65fbf7` | assert response.status_code == 500 |  |
| 2026-11-18T22:08:55+00:00 | red-corrected | 1 | 4.16 | `pytest -q tests/test_htmx_errors.py` | `b5ca78e982bcdc5c` | assert response.status_code == 500 |  |
| 2026-11-18T22:09:36+00:00 | red-final | 1 | 4.08 | `pytest -q tests/test_htmx_errors.py` | `7c72b06e58b55ec6` | assert response.status_code == 500 |  |
| 2026-11-18T22:09:55+00:00 | focused-green | 0 | 4.0 | `pytest -q tests/test_htmx_errors.py` | `9e7581cfbdec7e91` |  |  |
| 2026-11-18T22:10:00+00:00 | ui-all | 0 | 0.32 | `python .migration/harness/tools/check_ui.py --all` | `0cb805740bfb2d16` |  | gate=ui scope="every template" templates=21 findings=0 |
| 2026-11-18T22:10:39+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T22:10:45+00:00 | build-check | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T22:10:48+00:00 | ruff-check | 1 | 0.03 | `ruff check` | `618ca838ec8319d2` | Found 1 error. |  |
| 2026-11-18T22:10:57+00:00 | ruff-check-rerun | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T22:11:00+00:00 | ruff-format | 0 | 0.03 | `ruff format --check` | `02bed28762c49640` |  |  |
| 2026-11-18T22:11:11+00:00 | layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `59bfd54275a9b5a4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T22:11:15+00:00 | ui-changed | 0 | 0.35 | `python .migration/harness/tools/check_ui.py` | `ce9e0484bc0f7c63` |  | gate=ui scope="templates changed since origin/main" templates=2 findings=0 |
| 2026-11-18T22:12:47+00:00 | behavior | 0 | 88.21 | `pytest -q` | `1ac285edb426d33a` |  |  |
| 2026-11-18T22:14:18+00:00 | crap-coverage | 0 | 85.36 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `ab11dcae27a46363` |  |  |
| 2026-11-18T22:14:23+00:00 | crap-lizard | 0 | 0.18 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T22:14:27+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `dbeb57242d6b2a6b` |  | gate=crap max=26.0 threshold=30 over=0 methods=213 |
| 2026-11-18T22:14:32+00:00 | mutation-changed | 0 | 0.09 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-18T22:16:05+00:00 | regression | 0 | 76.14 | `pytest -q` | `c2aab12ea8c91682` |  |  |
| 2026-11-18T22:18:37+00:00 | focused-assertions | 0 | 4.0 | `pytest -q tests/test_htmx_errors.py` | `0f03d454dd7d0a3a` |  |  |
| 2026-11-18T22:18:41+00:00 | ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T22:18:45+00:00 | ruff-format-final | 0 | 0.01 | `ruff format --check` | `02bed28762c49640` |  |  |
| 2026-11-18T22:20:07+00:00 | regression-final | 0 | 75.53 | `pytest -q` | `b9b679cd673b15eb` |  |  |
| 2026-11-18T22:25:53+00:00 | focused-expired-cargo | 0 | 4.14 | `pytest -q tests/test_htmx_errors.py` | `7ded2b4efd0963a6` |  |  |
| 2026-11-18T22:25:58+00:00 | ruff-check-post-review | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T22:27:28+00:00 | regression-post-review | 0 | 85.3 | `pytest -q` | `eefdf9d8c6b07f3f` |  |  |
| 2026-11-18T22:30:50+00:00 | red-default-catchall | 1 | 4.13 | `pytest -q tests/test_htmx_errors.py` | `e6d4c22d349e6fa5` | assert response.status_code == 500 |  |
| 2026-11-18T22:31:10+00:00 | focused-final | 0 | 4.0 | `pytest -q tests/test_htmx_errors.py` | `0f03d454dd7d0a3a` |  |  |
| 2026-11-18T22:31:15+00:00 | ui-all-final | 0 | 0.35 | `python .migration/harness/tools/check_ui.py --all` | `0cb805740bfb2d16` |  | gate=ui scope="every template" templates=21 findings=0 |
| 2026-11-18T22:31:20+00:00 | build-compile-final | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T22:31:24+00:00 | build-check-final | 0 | 0.39 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T22:31:28+00:00 | ruff-check-final-v2 | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T22:31:33+00:00 | ruff-format-final-v2 | 0 | 0.01 | `ruff format --check` | `02bed28762c49640` |  |  |
| 2026-11-18T22:31:37+00:00 | layers-final | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `59bfd54275a9b5a4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T22:31:42+00:00 | ui-changed-final | 0 | 0.38 | `python .migration/harness/tools/check_ui.py` | `ce9e0484bc0f7c63` |  | gate=ui scope="templates changed since origin/main" templates=2 findings=0 |
| 2026-11-18T22:33:04+00:00 | behavior-final-v2 | 0 | 77.08 | `pytest -q` | `cccd3629c0d1340d` |  |  |
| 2026-11-18T22:34:25+00:00 | crap-coverage-final-v2 | 0 | 76.0 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `4b31854015afacd6` |  |  |
| 2026-11-18T22:34:30+00:00 | crap-lizard-final-v2 | 0 | 0.17 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T22:34:34+00:00 | crap-score-final-v2 | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `dbeb57242d6b2a6b` |  | gate=crap max=26.0 threshold=30 over=0 methods=213 |
| 2026-11-18T22:34:39+00:00 | mutation-changed-final-v2 | 0 | 0.08 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-18T22:36:02+00:00 | regression-final-v2 | 0 | 76.09 | `pytest -q` | `cb860d3b6d428cb1` |  |  |
| 2026-11-18T22:39:20+00:00 | verification-ui-all | 0 | 0.37 | `python .migration/harness/tools/check_ui.py --all` | `0cb805740bfb2d16` |  | gate=ui scope="every template" templates=21 findings=0 |
| 2026-11-18T22:40:54+00:00 | verification-regression | 0 | 90.92 | `pytest -q` | `0d7a19316c816193` |  |  |
| 2026-11-18T23:54:12+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T23:55:55+00:00 | red-live-map-opt-out | 1 | 4.13 | `pytest -q tests/test_htmx_errors.py::test_live_map_page_keeps_marker_errors_silent` | `2e167f3156e0eeb5` | assert b'name="htmx-config"' in page.content |  |
| 2026-11-18T23:56:06+00:00 | focused-map-silence | 0 | 1.58 | `pytest -q tests/test_htmx_errors.py::test_live_map_page_keeps_marker_errors_silent tests/test_htmx_errors.py::test_tracking_page_swaps_unknown_tracking_id_error` | `8467712def929e7a` |  |  |
| 2026-11-18T23:59:36+00:00 | lint-ruling | 1 | 0.07 | `bash -c 'ruff check && ruff format --check'` | `3722476becd67db0` | 36 \|     assert RESPONSE_HANDLING in page.content |  |
| 2026-11-18T23:59:37+00:00 | ui-all-ruling | 0 | 0.27 | `python .migration/harness/tools/check_ui.py --all` | `0cb805740bfb2d16` |  | gate=ui scope="every template" templates=21 findings=0 |
| 2026-11-18T23:59:41+00:00 | focused-map-error-coverage | 0 | 4.64 | `pytest -q tests/test_htmx_errors.py tests/cargo/interfaces/test_admin_live_map_markers.py tests/cargo/test_tracking.py` | `78a8bc349a60baa1` |  |  |
| 2026-11-19T00:00:01+00:00 | lint-ruling-final | 0 | 0.04 | `bash -c 'ruff check && ruff format --check'` | `de130d5f38e219d6` |  |  |
| 2026-11-19T00:00:01+00:00 | ui-all-ruling-final | 0 | 0.29 | `python .migration/harness/tools/check_ui.py --all` | `0cb805740bfb2d16` |  | gate=ui scope="every template" templates=21 findings=0 |
| 2026-11-19T00:00:05+00:00 | focused-ruling-final | 0 | 4.7 | `pytest -q tests/test_htmx_errors.py tests/cargo/interfaces/test_admin_live_map_markers.py tests/cargo/test_tracking.py` | `ac996c6dbbf1d588` |  |  |
