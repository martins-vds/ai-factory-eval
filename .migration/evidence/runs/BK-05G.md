# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:30:35+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:33:17+00:00 | destination-dialog-red | 2 | 2.41 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `194a6dff8cf11f73` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-22T17:33:48+00:00 | destination-dialog-green | 0 | 3.69 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `8cfb4ab9ca784248` |  |  |
| 2026-11-22T17:34:02+00:00 | destination-update-red | 1 | 2.4 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_update_preserves_other_specification_fields_and_refreshes_dashboard` | `266a132a77a1d304` | assert before is not None |  |
| 2026-11-22T17:34:15+00:00 | destination-update-green | 0 | 4.01 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `4056640ad4dc3f37` |  |  |
| 2026-11-22T17:34:27+00:00 | deadline-dialog-red | 4 | 0.91 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_deadline_dialog_shows_current_specification` | `c717685ff1ba5872` | ERROR: found no collectors for /home/runner/work/ai-factory-eval/ai-factory-eval/tests/booking/interfaces/test_dialogs.p |  |
| 2026-11-22T17:34:38+00:00 | deadline-dialog-green | 0 | 2.34 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_deadline_dialog_shows_current_specification` | `bbc4f2445a949664` |  |  |
| 2026-11-22T17:34:46+00:00 | deadline-parse-red | 1 | 2.4 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_invalid_deadline_is_reported_at_the_field_without_changing_cargo` | `99042684d2e183c9` | assert before is not None |  |
| 2026-11-22T17:34:57+00:00 | deadline-parse-green | 0 | 2.49 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_invalid_deadline_is_reported_at_the_field_without_changing_cargo` | `174f70b1d0fe89f1` |  |  |
| 2026-11-22T17:35:36+00:00 | dialog-workflow-targeted | 0 | 6.3 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `a6abd2a151c88686` |  |  |
| 2026-11-22T17:36:08+00:00 | dialog-workflow-regression | 1 | 7.78 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `501349cb079dd083` | assert response.status_code == 404 |  |
| 2026-11-22T17:36:23+00:00 | dialog-workflow-regression | 0 | 7.73 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `489ffc0f73b28920` |  |  |
| 2026-11-22T17:36:30+00:00 | ruff-check | 1 | 0.03 | `ruff check` | `10d014f86fb02fa6` | Found 1 error. |  |
| 2026-11-22T17:36:36+00:00 | ruff-format-check | 1 | 0.02 | `ruff format --check` | `de3f8cc3538d22fc` | 79  \|     assert updated.route_specification.destination.unlocode.value == 'USCHI' |  |
| 2026-11-22T17:36:41+00:00 | ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T17:36:43+00:00 | ruff-format-check | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-22T17:36:45+00:00 | layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-22T17:36:48+00:00 | ui-check | 0 | 0.69 | `python .migration/harness/tools/check_ui.py` | `c3dc6a5f7e106735` |  | gate=ui scope="templates changed since b3309f44a4a34d8fd929b76624590374d44a746f" templates=2 findings=0 |
| 2026-11-22T17:37:08+00:00 | not-found-fragment-red | 1 | 2.95 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_dialog_for_unknown_cargo_renders_not_found_response` | `5e05c551228e3ddb` | assert response.status_code == 404 |  |
| 2026-11-22T17:37:21+00:00 | not-found-fragment-green | 0 | 7.83 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `447cdca6b18af928` |  |  |
| 2026-11-22T17:39:36+00:00 | behavior | 0 | 7.62 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `9dd28b6d77427e6d` |  |  |
| 2026-11-22T17:39:40+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:39:43+00:00 | build-check | 0 | 0.37 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T17:39:45+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T17:39:48+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-22T17:39:50+00:00 | idiom-layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-22T17:39:53+00:00 | idiom-ui | 0 | 0.71 | `python .migration/harness/tools/check_ui.py` | `63d7cd2a007321d4` |  | gate=ui scope="templates changed since b3309f44a4a34d8fd929b76624590374d44a746f" templates=3 findings=0 |
| 2026-11-22T17:41:03+00:00 | crap-coverage | 0 | 65.86 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `c5c334ebc0b8c675` |  |  |
| 2026-11-22T17:41:19+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:41:22+00:00 | crap-threshold | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0d6078663616a9ed` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-22T17:43:56+00:00 | mutation-changed | 0 | 150.48 | `python .migration/harness/tools/afs-mutation` | `b87397bc2e1711f4` |  | gate=mutation score=0.833 threshold=0.8 killed=40 survived=8 files=1 base=b3309f44a4a34d8fd929b76624590374d44a746f |
| 2026-11-22T17:44:38+00:00 | behavior-mutant-coverage | 0 | 8.45 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `fa5b6e7a4bde2a93` |  |  |
| 2026-11-22T17:47:04+00:00 | mutation-changed | 0 | 143.24 | `python .migration/harness/tools/afs-mutation` | `ce9296c19d924400` |  | gate=mutation score=1.000 threshold=0.8 killed=48 survived=0 files=1 base=b3309f44a4a34d8fd929b76624590374d44a746f |
| 2026-11-22T17:47:20+00:00 | final-build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:47:25+00:00 | final-build-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T17:47:28+00:00 | final-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T17:47:31+00:00 | final-ruff-format | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-22T17:47:34+00:00 | final-layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-22T17:47:38+00:00 | final-ui | 0 | 0.7 | `python .migration/harness/tools/check_ui.py` | `63d7cd2a007321d4` |  | gate=ui scope="templates changed since b3309f44a4a34d8fd929b76624590374d44a746f" templates=3 findings=0 |
| 2026-11-22T17:47:49+00:00 | final-behavior | 0 | 8.57 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `8959ac94963a6641` |  |  |
| 2026-11-22T17:49:08+00:00 | final-crap-coverage | 0 | 73.82 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `35071b224590d47a` |  |  |
| 2026-11-22T17:49:17+00:00 | final-ui-after-a11y | 0 | 0.71 | `python .migration/harness/tools/check_ui.py` | `63d7cd2a007321d4` |  | gate=ui scope="templates changed since b3309f44a4a34d8fd929b76624590374d44a746f" templates=3 findings=0 |
| 2026-11-22T17:49:20+00:00 | final-crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:49:25+00:00 | final-crap-threshold | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0d6078663616a9ed` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-22T17:49:47+00:00 | final-behavior | 0 | 8.5 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `707f20b3419e1680` |  |  |
| 2026-11-22T17:50:52+00:00 | regression | 0 | 62.47 | `pytest -q` | `6e0519bd410c813b` |  |  |
