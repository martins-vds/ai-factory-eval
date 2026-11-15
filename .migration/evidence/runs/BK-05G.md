# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T07:07:59+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T07:08:12+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T07:10:23+00:00 | bk05e-dashboard-regression | 0 | 2.53 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `6343dd31090b1c8a` |  |  |
| 2026-11-15T07:13:13+00:00 | destination-dialog-red | 4 | 0.52 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_shows_current_values_and_stable_filtered_options` | `4ecd2ae60706e49b` | ERROR: found no collectors for /home/runner/work/ai-factory-eval/ai-factory-eval/tests/booking/interfaces/test_dialogs.p |  |
| 2026-11-15T07:13:57+00:00 | destination-dialog-green | 0 | 1.32 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_shows_current_values_and_stable_filtered_options` | `7ed2738ac3dcd8f9` |  |  |
| 2026-11-15T07:14:40+00:00 | deadline-dialog-red | 1 | 1.41 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_deadline_dialog_shows_current_route_and_deadline` | `84aff0dc9956f8cb` | /opt/hostedtoolcache/Python/3.13.18/x64/lib/python3.13/site-packages/django/core/handlers/exception.py:55: in inner |  |
| 2026-11-15T07:14:55+00:00 | deadline-dialog-green | 0 | 1.32 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_deadline_dialog_shows_current_route_and_deadline` | `7b23e52dabef120c` |  |  |
| 2026-11-15T07:15:07+00:00 | deadline-parse-red | 1 | 1.36 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_deadline_dialog_reports_a_field_error_for_unparseable_date` | `786e18b491674d23` | assert response.status_code == 200 |  |
| 2026-11-15T07:15:39+00:00 | deadline-parse-green | 1 | 1.45 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_deadline_dialog_reports_a_field_error_for_unparseable_date` | `3632d2fb53049300` | assert response.status_code == 200 |  |
| 2026-11-15T07:15:53+00:00 | deadline-parse-green | 0 | 1.4 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_deadline_dialog_reports_a_field_error_for_unparseable_date` | `b29404b0332b987b` |  |  |
| 2026-11-15T07:16:12+00:00 | destination-update-test | 0 | 1.45 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_update_preserves_other_specification_fields_and_refreshes` | `b29404b0332b987b` |  |  |
| 2026-11-15T07:16:24+00:00 | deadline-update-test | 0 | 1.4 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_deadline_dialog_update_preserves_route_and_refreshes` | `313e5831c83bcc34` |  |  |
| 2026-11-15T07:16:38+00:00 | dialog-cancel-red | 1 | 1.56 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_cancel_dialog_closes_without_updating_cargo` | `2b8a52a73e4673fb` | assert cargo_before is not None |  |
| 2026-11-15T07:16:48+00:00 | dialog-cancel-green | 0 | 1.55 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_cancel_dialog_closes_without_updating_cargo` | `ca3473021cd297f2` |  |  |
| 2026-11-15T07:17:03+00:00 | table-dialog-links-red | 1 | 1.29 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_opens_destination_and_deadline_dialogs` | `587f9ab1fed180dc` | assert response.status_code == 200 |  |
| 2026-11-15T07:17:17+00:00 | table-dialog-links-green | 0 | 1.34 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_opens_destination_and_deadline_dialogs` | `baa6efe8d11cd56d` |  |  |
| 2026-11-15T07:17:41+00:00 | direct-dialog-page-red | 1 | 1.42 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_direct_dialog_link_renders_a_dashboard_page_without_htmx` | `33c4a955bc77b0a3` | assert response.status_code == 200 |  |
| 2026-11-15T07:17:58+00:00 | direct-dialog-page-green | 0 | 1.4 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_direct_dialog_link_renders_a_dashboard_page_without_htmx` | `7b23e52dabef120c` |  |  |
| 2026-11-15T07:18:15+00:00 | dialogs-tests | 0 | 3.44 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `5375539cbcc8d899` |  |  |
| 2026-11-15T07:18:22+00:00 | bk05e-dashboard-regression | 0 | 1.69 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `89db3b8e278b18c8` |  |  |
