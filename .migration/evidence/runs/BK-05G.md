# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:41:20+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:44:15+00:00 | table-actions-red | 1 | 2.66 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_opens_destination_and_deadline_dialogs` | `a0fcb746f97fa8fe` | assert cargo is not None |  |
| 2026-11-22T17:44:28+00:00 | table-actions-green | 0 | 2.24 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_opens_destination_and_deadline_dialogs` | `f71b6d40f60d9414` |  |  |
| 2026-11-22T17:45:08+00:00 | destination-dialog-red | 4 | 0.85 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_displays_current_route_and_filters_options_stably` | `09a3e89398a2d1f3` | ERROR: found no collectors for /home/runner/work/ai-factory-eval/ai-factory-eval/tests/booking/interfaces/test_dialogs.p |  |
| 2026-11-22T17:45:49+00:00 | destination-dialog-green | 1 | 2.25 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_displays_current_route_and_filters_options_stably` | `b0603b4e0eb68ce0` | E       TypeError: create_dialog_views.<locals>.destination_dialog() missing 1 required positional argument: 'tracking_i |  |
| 2026-11-22T17:45:56+00:00 | destination-dialog-green | 1 | 2.32 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_displays_current_route_and_filters_options_stably` | `0af9f16d57bc263b` | assert all(response.status_code == 200 for response in responses) |  |
| 2026-11-22T17:46:06+00:00 | destination-dialog-green | 0 | 2.29 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_displays_current_route_and_filters_options_stably` | `bbc4f2445a949664` |  |  |
| 2026-11-22T17:46:20+00:00 | destination-update | 0 | 2.33 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_updates_cargo_and_completes_htmx_dialog` | `448843cb5dffaeac` |  |  |
| 2026-11-22T17:47:04+00:00 | dialogs-targeted | 0 | 5.79 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `03d664028c95c5a7` |  |  |
| 2026-11-22T17:47:46+00:00 | dialogs-http-flow | 0 | 2.42 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_opens_destination_and_deadline_dialogs` | `8ca7534279cbd21c` |  |  |
| 2026-11-22T17:48:04+00:00 | lint-check | 1 | 0.03 | `ruff check` | `93e89eb45d217f35` | Found 1 error. |  |
| 2026-11-22T17:49:15+00:00 | lint-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T17:49:17+00:00 | format-check | 1 | 0.02 | `ruff format --check` | `d4fb4b36d3116b83` | 145 \|     assert 'Melbourne' in content |  |
| 2026-11-22T17:49:31+00:00 | dialogs-targeted | 0 | 5.58 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `5a4d2ea9e50bfd83` |  |  |
| 2026-11-22T17:49:34+00:00 | format-check | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-22T17:50:16+00:00 | dialogs-targeted | 1 | 6.91 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `b7981292c327bec7` | deadline = 'not-a-date', error = 'Enter a valid arrival deadline.' |  |
| 2026-11-22T17:50:51+00:00 | dialogs-targeted | 0 | 7.3 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `24a72d3b2322d4b5` |  |  |
