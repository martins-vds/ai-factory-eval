# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:09:22+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:12:31+00:00 | red-not-routed-dialogs | 1 | 4.11 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `45dc11af28c1fcb9` | assert response.status_code == 200 |  |
| 2026-11-18T13:12:45+00:00 | table-dialog-actions | 0 | 2.25 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ac66644beec34f95` |  |  |
| 2026-11-18T13:13:44+00:00 | red-deadline-dialog | 2 | 1.03 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2cdd555a509d025d` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T13:14:15+00:00 | deadline-dialog-initial | 0 | 2.69 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `7f126ac6f686566f` |  |  |
| 2026-11-18T13:14:33+00:00 | deadline-dialog-updates | 0 | 4.08 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ce8ef0d053dd4628` |  |  |
| 2026-11-18T13:14:49+00:00 | red-destination-dialog | 2 | 1.05 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0f71c778f8ee8b60` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T13:15:10+00:00 | dialog-boundary | 0 | 4.53 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `5a0254c92f330ccc` |  |  |
| 2026-11-18T13:15:54+00:00 | dialog-rules | 0 | 6.81 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `4d1e1c40bf883304` |  |  |
| 2026-11-18T13:16:43+00:00 | dashboard-regression | 0 | 2.78 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `c6610adf5a0df7e8` |  |  |
| 2026-11-18T13:17:27+00:00 | lint-dialogs | 1 | 0.01 | `ruff check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `fb955a9f84fc3bbc` | Found 1 error. |  |
| 2026-11-18T13:17:35+00:00 | format-dialogs | 1 | 0.01 | `ruff format --check src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `cf7d0d0a4676442b` | 127 \|     assert cargo_after.route_specification.origin == cargo_before.route_specification.origin |  |
| 2026-11-18T13:17:42+00:00 | layers-dialogs | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T13:17:46+00:00 | ui-dialogs | 1 | 0.51 | `python .migration/harness/tools/check_ui.py` | `dbbf35ebbfd57ed4` | templates/booking/dashboard/not_routed_table.html:34: sends an htmx request ('hx-get'), but nothing handles error respon | gate=ui scope="templates changed since f6dba3f598ee61a507ad97635f5a6d042459cfe6" templates=5 findings=3 |
| 2026-11-18T13:18:29+00:00 | ui-dialogs-handled | 0 | 0.48 | `python .migration/harness/tools/check_ui.py` | `b0eb3e8a7f5c0872` |  | gate=ui scope="templates changed since f6dba3f598ee61a507ad97635f5a6d042459cfe6" templates=6 findings=0 |
| 2026-11-18T13:18:41+00:00 | dialogs-after-errors | 1 | 8.01 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `33675ecdd8fb6af9` | assert response.status_code == 200 |  |
| 2026-11-18T13:18:58+00:00 | dialogs-after-errors-fixed | 0 | 7.92 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `7a87546d53dc998d` |  |  |
| 2026-11-18T13:19:38+00:00 | red-noncanonical-deadline | 1 | 2.87 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_deadline_dialog_reports_an_invalid_date_without_changing_cargo` | `d30d263f7343d07d` | assert cargo_before is not None |  |
| 2026-11-18T13:19:50+00:00 | deadline-format-strict | 0 | 2.72 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_deadline_dialog_reports_an_invalid_date_without_changing_cargo` | `f2b257cf6a1c3718` |  |  |
| 2026-11-18T13:20:58+00:00 | accessible-dialog-tests | 0 | 8.43 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `6e345db1057e671d` |  |  |
| 2026-11-18T13:21:02+00:00 | ui-dialogs-modal | 0 | 0.49 | `python .migration/harness/tools/check_ui.py` | `b0eb3e8a7f5c0872` |  | gate=ui scope="templates changed since f6dba3f598ee61a507ad97635f5a6d042459cfe6" templates=6 findings=0 |
