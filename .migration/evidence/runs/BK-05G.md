# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:14:06+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:17:36+00:00 | tdd-red-destination | 2 | 3.34 | `pytest -q tests/booking/interfaces/test_dialogs.py -k destination_dialog_excludes_origin_and_current_destination_without_mutating_locations` | `23ce79c7d0481ba1` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-19T18:18:01+00:00 | tdd-green-destination | 0 | 2.29 | `pytest -q tests/booking/interfaces/test_dialogs.py -k destination_dialog_excludes_origin_and_current_destination_without_mutating_locations` | `48d1e350f94062d9` |  |  |
| 2026-11-19T18:18:24+00:00 | tdd-red-deadline | 1 | 2.27 | `pytest -q tests/booking/interfaces/test_dialogs.py -k invalid_deadline_shows_field_error_and_keeps_entered_value` | `aaa5664b552c814f` | assert response.status_code == 200 |  |
| 2026-11-19T18:18:43+00:00 | tdd-green-deadline | 0 | 2.23 | `pytest -q tests/booking/interfaces/test_dialogs.py -k invalid_deadline_shows_field_error_and_keeps_entered_value` | `925eefb519fd955b` |  |  |
| 2026-11-19T18:18:59+00:00 | tdd-deadline-update | 0 | 2.34 | `pytest -q tests/booking/interfaces/test_dialogs.py -k deadline_update_preserves_other_route_specification_fields_and_redirects` | `0b9fbe10699675d7` |  |  |
| 2026-11-19T18:19:16+00:00 | tdd-red-destination-update | 1 | 2.3 | `pytest -q tests/booking/interfaces/test_dialogs.py -k destination_update_preserves_other_route_specification_fields_and_redirects` | `3ff7efb0ad7c0070` | assert cargo_before is not None |  |
| 2026-11-19T18:19:30+00:00 | tdd-green-destination-update | 0 | 2.21 | `pytest -q tests/booking/interfaces/test_dialogs.py -k destination_update_preserves_other_route_specification_fields_and_redirects` | `ea177c190e166654` |  |  |
| 2026-11-19T18:19:49+00:00 | tdd-red-table-triggers | 1 | 2.19 | `pytest -q tests/booking/interfaces/test_dialogs.py -k not_routed_table_opens_destination_and_deadline_dialogs` | `1a3daa7009b85710` | assert 'href="/admin/cargo/DEF789/route/"' in content |  |
| 2026-11-19T18:20:11+00:00 | tdd-green-table-triggers | 0 | 2.13 | `pytest -q tests/booking/interfaces/test_dialogs.py -k not_routed_table_opens_destination_and_deadline_dialogs` | `2b678cb62dc9e212` |  |  |
| 2026-11-19T18:20:37+00:00 | dialogs-targeted | 1 | 4.57 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `9dda32ca554f3043` | assert response.status_code == 200 |  |
| 2026-11-19T18:20:54+00:00 | dialogs-targeted | 0 | 4.35 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `16cd6133529bb348` |  |  |
| 2026-11-19T18:21:29+00:00 | focused-regression | 0 | 5.49 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `117fea6583e457b3` |  |  |
| 2026-11-19T18:21:50+00:00 | focused-regression | 0 | 5.52 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `117fea6583e457b3` |  |  |
| 2026-11-19T18:23:05+00:00 | dialogs-http-e2e | 0 | 2.26 | `pytest -q tests/booking/interfaces/test_dialogs.py -k http_flow_opens_updates_and_refreshes_destination_dialog` | `d409d8c634e77506` |  |  |
| 2026-11-19T18:24:11+00:00 | ruff-check | 1 | 0.03 | `ruff check` | `1c423fec1b999e4c` | Found 1 error. |  |
| 2026-11-19T18:24:20+00:00 | ruff-format | 1 | 0.02 | `ruff format --check` | `eff85aaab27f6553` |  |  |
| 2026-11-19T18:24:27+00:00 | ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:24:32+00:00 | ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T18:24:36+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:24:40+00:00 | build-check | 0 | 0.37 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T18:24:44+00:00 | layers | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T18:24:48+00:00 | ui | 0 | 0.46 | `python .migration/harness/tools/check_ui.py` | `5b36987a8a5d8b09` |  | gate=ui scope="templates changed since 38ac36c4838555c7db2eb9ef3e243981b571e9f1" templates=3 findings=0 |
| 2026-11-19T18:25:55+00:00 | behavior | 0 | 62.72 | `pytest -q` | `44a2d97270319074` |  |  |
| 2026-11-19T18:27:04+00:00 | crap-coverage | 0 | 61.37 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `0e037e61c118a994` |  |  |
| 2026-11-19T18:27:08+00:00 | crap-lizard | 0 | 0.14 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:27:12+00:00 | crap | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `af17a1a7cca8a5c4` |  | gate=crap max=26.0 threshold=30 over=0 methods=204 |
| 2026-11-19T18:29:36+00:00 | mutation_changed | 1 | 138.88 | `python .migration/harness/tools/afs-mutation` | `37193e6d9ecd0af8` | afs-mutation: FAILED score=0.692 threshold=0.8 killed=36 survived=16 skipped=0 files=1 jobs=1 base=38ac36c4838555c7db2eb | gate=mutation score=0.692 threshold=0.8 killed=36 survived=16 files=1 base=38ac36c4838555c7db2eb9ef3e243981b571e9f1 |
| 2026-11-19T18:30:50+00:00 | strengthened-tests | 0 | 7.23 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `a9f6498ebe4cf267` |  |  |
| 2026-11-19T18:33:29+00:00 | mutation_changed | 0 | 134.63 | `python .migration/harness/tools/afs-mutation` | `20ed9e4b3a48b7be` |  | gate=mutation score=0.837 threshold=0.8 killed=41 survived=8 files=1 base=38ac36c4838555c7db2eb9ef3e243981b571e9f1 |
| 2026-11-19T18:39:18+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:39:22+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T18:39:28+00:00 | ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:39:31+00:00 | ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T18:39:35+00:00 | layers | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T18:39:39+00:00 | ui | 0 | 0.47 | `python .migration/harness/tools/check_ui.py` | `5b36987a8a5d8b09` |  | gate=ui scope="templates changed since 38ac36c4838555c7db2eb9ef3e243981b571e9f1" templates=3 findings=0 |
| 2026-11-19T18:40:43+00:00 | behavior | 0 | 59.83 | `pytest -q` | `9e58932ded1a3125` |  |  |
| 2026-11-19T18:41:52+00:00 | crap-coverage | 0 | 58.12 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `334ea18c0617e902` |  |  |
| 2026-11-19T18:41:55+00:00 | crap-lizard | 0 | 0.13 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:42:00+00:00 | crap | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `222c126af9b750bd` |  | gate=crap max=26.0 threshold=30 over=0 methods=204 |
| 2026-11-19T18:43:05+00:00 | regression | 0 | 60.0 | `pytest -q` | `6a2dc898b872f34b` |  |  |
