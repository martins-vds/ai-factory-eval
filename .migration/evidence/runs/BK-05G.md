# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:17:15+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:21:04+00:00 | test-table-dialog-controls-red | 1 | 3.38 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_exposes_dialog_controls_without_changing_route_link` | `f9d2fa26402f9a10` | assert response.status_code == 200 |  |
| 2026-11-19T18:21:44+00:00 | test-table-dialog-controls-green | 0 | 1.59 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_exposes_dialog_controls_without_changing_route_link` | `941ba30613647e4a` |  |  |
| 2026-11-19T18:22:23+00:00 | test-destination-dialog-red | 4 | 0.82 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_filters_options_without_mutating_locations` | `05ad4f3f8d2d1ca1` | ERROR: found no collectors for /home/runner/work/ai-factory-eval/ai-factory-eval/tests/booking/interfaces/test_dialogs.p |  |
| 2026-11-19T18:22:56+00:00 | test-destination-dialog-options | 0 | 1.65 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_destination_dialog_filters_options_without_mutating_locations` | `592eda075adf20a2` |  |  |
| 2026-11-19T18:23:28+00:00 | dialogs-targeted | 0 | 4.64 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `e9066841e9b6f962` |  |  |
| 2026-11-19T18:24:01+00:00 | bk05e-and-specification-regression | 0 | 2.06 | `pytest -q tests/booking/interfaces/test_dashboard.py tests/booking/application/test_specification.py` | `d03219206b918765` |  |  |
| 2026-11-19T18:24:48+00:00 | specification-rule-tests | 0 | 1.7 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_change_destination_use_case_rejects_the_cargo_origin tests/booking/interfaces/test_dialogs.py::test_change_deadline_use_case_rejects_non_datetime_input` | `e8bd98ab1634e9c9` |  |  |
| 2026-11-19T18:27:55+00:00 | behavior | 0 | 5.79 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py tests/booking/application/test_specification.py` | `8df803c62740b2c9` |  |  |
| 2026-11-19T18:28:00+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:28:03+00:00 | build-django-check | 0 | 0.27 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T18:28:06+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:28:10+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T18:28:13+00:00 | idiom-layers | 0 | 0.1 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T18:28:17+00:00 | idiom-ui | 0 | 0.35 | `python .migration/harness/tools/check_ui.py` | `6e67a5a00e6e91f8` |  | gate=ui scope="templates changed since ce761d4a65447f021ae8d498bada3ebbdc42c352" templates=3 findings=0 |
| 2026-11-19T18:28:59+00:00 | crap-coverage | 0 | 38.81 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `e94ffba5530af342` |  |  |
| 2026-11-19T18:29:04+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:29:07+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `42b637de9cb6ebca` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-19T18:29:52+00:00 | regression | 0 | 40.07 | `pytest -q` | `d0cbea4f20e25dfb` |  |  |
| 2026-11-19T18:31:40+00:00 | mutation-changed | 0 | 103.0 | `python .migration/harness/tools/afs-mutation` | `5880cfd49bc04ab7` |  | gate=mutation score=0.891 threshold=0.8 killed=49 survived=6 files=1 base=ce761d4a65447f021ae8d498bada3ebbdc42c352 |
| 2026-11-19T18:34:01+00:00 | behavior | 0 | 5.53 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py tests/booking/application/test_specification.py` | `9d6ad0bd01d39f47` |  |  |
| 2026-11-19T18:34:05+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:34:08+00:00 | build-django-check | 0 | 0.26 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T18:34:12+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:34:17+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T18:34:22+00:00 | idiom-layers | 0 | 0.1 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T18:34:26+00:00 | idiom-ui | 0 | 0.33 | `python .migration/harness/tools/check_ui.py` | `6e67a5a00e6e91f8` |  | gate=ui scope="templates changed since ce761d4a65447f021ae8d498bada3ebbdc42c352" templates=3 findings=0 |
| 2026-11-19T18:35:09+00:00 | crap-coverage | 0 | 39.47 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `480927577cf8dd7b` |  |  |
| 2026-11-19T18:35:13+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:35:16+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `42b637de9cb6ebca` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-19T18:35:59+00:00 | regression | 0 | 37.98 | `pytest -q` | `20ad698b1263b6eb` |  |  |
| 2026-11-19T18:37:40+00:00 | mutation-changed | 0 | 95.77 | `python .migration/harness/tools/afs-mutation` | `cc57262d0b4c8f90` |  | gate=mutation score=0.945 threshold=0.8 killed=52 survived=3 files=1 base=ce761d4a65447f021ae8d498bada3ebbdc42c352 |
