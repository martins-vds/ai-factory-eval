# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T18:53:06+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T18:57:28+00:00 | red-destination-initial | 4 | 2.68 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_shows_initial_values_and_stable_filtered_options` | `cd3278f3bdc38592` | ERROR: found no collectors for /home/runner/work/ai-factory-eval/ai-factory-eval/tests/booking/interfaces/test_dialogs.p |  |
| 2026-11-21T18:58:26+00:00 | behavior-dialog-initial | 0 | 3.17 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_shows_initial_values_and_stable_filtered_options tests/booking/interfaces/test_dialogs.py::test_deadline_dialog_shows_cargo_route_fields_and_current_deadline` | `dfc416a005792190` |  |  |
| 2026-11-21T18:58:56+00:00 | red-deadline-parse | 1 | 2.4 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_unparseable_deadline_is_reported_at_the_deadline_field` | `cfa109bcef963960` | assert original is not None |  |
| 2026-11-21T18:59:09+00:00 | behavior-deadline-parse | 0 | 2.33 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_unparseable_deadline_is_reported_at_the_deadline_field` | `9d3563765210c96d` |  |  |
| 2026-11-21T18:59:22+00:00 | red-destination-update | 1 | 2.49 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_update_completes_dialog_and_refreshes_the_not_routed_row` | `bf245aded69a53cf` | assert original is not None |  |
| 2026-11-21T18:59:36+00:00 | behavior-destination-update | 1 | 2.42 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_update_completes_dialog_and_refreshes_the_not_routed_row` | `2415748ebd2872e3` | assert original is not None |  |
| 2026-11-21T18:59:48+00:00 | behavior-destination-update | 0 | 2.53 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_update_completes_dialog_and_refreshes_the_not_routed_row` | `9079c917b3657ef1` |  |  |
| 2026-11-21T18:59:58+00:00 | red-deadline-update | 1 | 2.6 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_deadline_update_completes_dialog_and_refreshes_the_not_routed_row` | `72e02a0328cf01fd` | assert original is not None |  |
| 2026-11-21T19:00:11+00:00 | behavior-deadline-update | 0 | 3.1 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_unparseable_deadline_is_reported_at_the_deadline_field tests/booking/interfaces/test_dialogs.py::test_deadline_update_completes_dialog_and_refreshes_the_not_routed_row` | `f8110290b7ac52b7` |  |  |
| 2026-11-21T19:00:29+00:00 | red-dialog-table-actions | 1 | 2.58 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_opens_edit_dialogs_and_refreshes_after_completion` | `c7d148f599e9b8a1` | assert response.status_code == 200 |  |
| 2026-11-21T19:00:42+00:00 | behavior-dialog-table-actions | 0 | 3.43 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_opens_edit_dialogs_and_refreshes_after_completion tests/booking/interfaces/test_dashboard.py` | `5890b2141684f73e` |  |  |
| 2026-11-21T19:00:51+00:00 | behavior-dialogs | 0 | 4.87 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a1f18e207a0e664b` |  |  |
| 2026-11-21T19:02:09+00:00 | red-dialog-focus | 1 | 2.49 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_opens_edit_dialogs_and_refreshes_after_completion` | `027a282c4d9695ae` | assert response.status_code == 200 |  |
| 2026-11-21T19:02:21+00:00 | behavior-dialog-validation-and-modal | 0 | 5.38 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0e7fcb69cc0df66e` |  |  |
| 2026-11-21T19:03:18+00:00 | behavior-dialogs-final | 0 | 7.86 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `1d7eb1eba1907233` |  |  |
| 2026-11-21T19:03:33+00:00 | lint-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T19:03:36+00:00 | lint-ruff-format | 1 | 0.02 | `ruff format --check` | `7baf063c29606c0a` | 59  \|     assert locations == initial_locations |  |
| 2026-11-21T19:03:43+00:00 | lint-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T19:06:03+00:00 | ledger-validation | 0 | 5.96 | `python .migration/harness/tools/validate.py .migration` | `6fb607b073658220` |  |  |
| 2026-11-21T19:07:12+00:00 | ui-check-current | 0 | 0.66 | `python .migration/harness/tools/check_ui.py` | `f703d528e362a4fa` |  | gate=ui scope="templates changed since 715133b6d39c3c7e9d5a0ead603b7c04446096df" templates=3 findings=0 |
| 2026-11-21T19:07:24+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T19:07:26+00:00 | build-django-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T19:07:28+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T19:07:31+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T19:07:34+00:00 | idiom-layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T19:07:37+00:00 | idiom-ui | 0 | 0.64 | `python .migration/harness/tools/check_ui.py` | `f703d528e362a4fa` |  | gate=ui scope="templates changed since 715133b6d39c3c7e9d5a0ead603b7c04446096df" templates=3 findings=0 |
| 2026-11-21T19:08:46+00:00 | behavior | 0 | 66.06 | `pytest -q` | `f7a4d57d40be455d` |  |  |
| 2026-11-21T19:09:53+00:00 | crap-coverage-tests | 0 | 62.94 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `2e5b258e32f544ec` |  |  |
| 2026-11-21T19:09:56+00:00 | crap-lizard | 0 | 0.17 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T19:09:58+00:00 | crap-threshold | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `27318cd287f5fcd4` |  | gate=crap max=26.0 threshold=30 over=0 methods=204 |
| 2026-11-21T19:13:00+00:00 | mutation-changed | 1 | 153.98 | `python .migration/harness/tools/afs-mutation` | `d97589e792c3a5fa` | afs-mutation: FAILED score=0.784 threshold=0.8 killed=40 survived=11 skipped=0 files=1 jobs=1 base=715133b6d39c3c7e9d5a0 | gate=mutation score=0.784 threshold=0.8 killed=40 survived=11 files=1 base=715133b6d39c3c7e9d5a0ead603b7c04446096df |
