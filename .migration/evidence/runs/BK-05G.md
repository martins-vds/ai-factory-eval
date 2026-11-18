# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:08:22+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:11:54+00:00 | not-routed-dialogs-red | 1 | 3.32 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `bd6233e2ba78cad5` | assert response.status_code == 200 |  |
| 2026-11-18T03:12:06+00:00 | not-routed-dialogs-green | 0 | 1.77 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `3c243acc54e1579e` |  |  |
| 2026-11-18T03:12:53+00:00 | destination-dialog-red | 2 | 0.83 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `11d5c63ccf647a52` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T03:13:27+00:00 | destination-dialog-green | 0 | 2.1 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2a7906a7fd573f02` |  |  |
| 2026-11-18T03:13:43+00:00 | destination-update-red | 2 | 0.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c10daeada2d14298` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T03:14:02+00:00 | destination-update-green | 0 | 2.55 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `bb58c735680539ed` |  |  |
| 2026-11-18T03:14:27+00:00 | deadline-dialog-red | 2 | 0.87 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `fd3310cf9ecbf78d` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T03:14:49+00:00 | deadline-dialog-green | 0 | 2.96 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `52300d8a03ea48d5` |  |  |
| 2026-11-18T03:15:07+00:00 | deadline-update | 0 | 3.39 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8f9bc6e76362d100` |  |  |
| 2026-11-18T03:15:53+00:00 | dialog-error-paths | 0 | 3.79 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8a60b1498003d628` |  |  |
| 2026-11-18T03:16:24+00:00 | destination-options | 0 | 3.75 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `48411b74e3199e02` |  |  |
| 2026-11-18T03:16:53+00:00 | destination-error-swap-red | 1 | 1.93 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_rejects_locations_outside_the_filtered_options` | `f13db6cafb9d49ed` | assert cargo is not None |  |
| 2026-11-18T03:17:11+00:00 | dialogs-targeted | 1 | 4.48 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `824b5cd6cfb8c29c` | assert cargo is not None |  |
| 2026-11-18T03:17:24+00:00 | dialogs-targeted-rerun | 0 | 4.56 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `ac22d6cc3e5a3152` |  |  |
| 2026-11-18T03:18:36+00:00 | dialogs-targeted-final | 0 | 4.7 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `0811ce6026dd74b6` |  |  |
| 2026-11-18T03:19:32+00:00 | dialogs-targeted-complete | 0 | 4.71 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `bc2a7de155000386` |  |  |
| 2026-11-18T03:22:44+00:00 | build | 0 | 0.52 | `bash -lc 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-18T03:22:47+00:00 | idiom | 1 | 0.21 | `bash -lc 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `a9862e5980e8d180` |  |  |
| 2026-11-18T03:23:01+00:00 | idiom | 1 | 0.7 | `bash -lc 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `dc0b5f17075169e0` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=ui scope="templates changed since a4f09948979d1e2e885f57feed762dc48e6c968f" templates=3 findings=3 |
| 2026-11-18T03:23:53+00:00 | stale-dialog-error-red | 1 | 1.56 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_dialogs_return_not_found_for_unknown_cargo` | `fe8fec2f632e12c2` | assert response.status_code == 404 |  |
| 2026-11-18T03:24:12+00:00 | stale-dialog-error-green | 0 | 3.91 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `dee9af3eb0ffa744` |  |  |
| 2026-11-18T03:24:16+00:00 | idiom | 0 | 0.69 | `bash -lc 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `0ece3651b7829fd8` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=ui scope="templates changed since a4f09948979d1e2e885f57feed762dc48e6c968f" templates=4 findings=0 |
