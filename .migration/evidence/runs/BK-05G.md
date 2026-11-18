# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:40:22+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:43:19+00:00 | behavior-red | 2 | 2.71 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8e9dc4d3d2b73809` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T12:44:52+00:00 | destination-get-green | 0 | 2.41 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `9079c917b3657ef1` |  |  |
| 2026-11-18T12:45:18+00:00 | deadline-get-red | 2 | 0.94 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0da0825529419e67` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T12:45:36+00:00 | deadline-get-green | 0 | 2.71 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `770f62c2fcfb7714` |  |  |
| 2026-11-18T12:46:00+00:00 | deadline-validation-red | 2 | 0.95 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `1ec4f25e9da991e2` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T12:46:26+00:00 | deadline-validation-green | 0 | 3.3 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `16ea4f870f6be017` |  |  |
| 2026-11-18T12:46:52+00:00 | deadline-update-green | 0 | 3.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8e75ad31b1f8847b` |  |  |
| 2026-11-18T12:47:21+00:00 | destination-update-red | 2 | 0.97 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `6bcb2598bff2f6b2` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T12:47:42+00:00 | destination-update-green | 1 | 4.3 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8ec3e89232996f26` | assert response.status_code == 200 |  |
| 2026-11-18T12:47:54+00:00 | destination-update-green-retry | 0 | 4.3 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a3cda5da27ccfe0a` |  |  |
| 2026-11-18T12:48:22+00:00 | table-dialog-triggers-red | 1 | 2.35 | `pytest -q tests/booking/interfaces/test_dialogs.py -k not_routed_table_opens` | `32e51df1d31a4fcc` | assert response.status_code == 200 |  |
| 2026-11-18T12:48:50+00:00 | dialogs-and-dashboard-green | 0 | 5.78 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `846032b0b45931c5` |  |  |
| 2026-11-18T12:49:31+00:00 | destination-reject-invalid | 0 | 5.23 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `bd46483470296c83` |  |  |
| 2026-11-18T12:50:23+00:00 | dialogs-dashboard-regression | 0 | 6.17 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `0eeaff76b71bd83d` |  |  |
| 2026-11-18T12:52:58+00:00 | modal-accessibility-regression | 0 | 5.9 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `fff0016f1a1c6b54` |  |  |
| 2026-11-18T12:53:16+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:53:20+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T12:53:31+00:00 | behavior | 0 | 6.18 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `8e920acb5e89fb09` |  |  |
| 2026-11-18T12:53:34+00:00 | idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:53:36+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `40254b6ecef96878` |  |  |
| 2026-11-18T12:53:42+00:00 | idiom-format-fix | 0 | 0.01 | `ruff format src/cargotracker/booking/interfaces/dialogs/views.py tests/booking/interfaces/test_dialogs.py` | `96a977f329ec3c59` |  |  |
| 2026-11-18T12:53:45+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T12:53:48+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T12:53:52+00:00 | idiom-ui | 1 | 0.53 | `python .migration/harness/tools/check_ui.py` | `e2609c90d69f3f3a` | templates/booking/dashboard/not_routed_table.html:35: sends an htmx request ('hx-get'), but nothing handles error respon | gate=ui scope="templates changed since 517bb57243bf7ca8848488a0f2ee96259892be95" templates=3 findings=3 |
| 2026-11-18T12:54:40+00:00 | idiom-ui-retry | 0 | 0.53 | `python .migration/harness/tools/check_ui.py` | `028090431a3e6ad6` |  | gate=ui scope="templates changed since 517bb57243bf7ca8848488a0f2ee96259892be95" templates=3 findings=0 |
| 2026-11-18T12:54:51+00:00 | behavior-after-ui-fix | 0 | 6.23 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `bcca4dc07217a9c1` |  |  |
| 2026-11-18T12:55:34+00:00 | behavior-unknown-cargo | 0 | 6.09 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `4904a2f52de74e3e` |  |  |
