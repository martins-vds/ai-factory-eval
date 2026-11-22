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
| 2026-11-22T17:53:04+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:53:08+00:00 | build-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T17:53:11+00:00 | lint-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T17:53:14+00:00 | format-check | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-22T17:53:17+00:00 | layers-check | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-22T17:53:21+00:00 | ui-check | 0 | 0.71 | `python .migration/harness/tools/check_ui.py` | `1d5399c7b667e826` |  | gate=ui scope="templates changed since 69441c3a713bf54fcd5c5986d77603941a984e6d" templates=3 findings=0 |
| 2026-11-22T17:54:29+00:00 | behavior-regression | 0 | 64.72 | `pytest -q` | `31fa2f4a2f11167a` |  |  |
| 2026-11-22T17:55:35+00:00 | crap-coverage | 0 | 61.44 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `c2444f317a290a32` |  |  |
| 2026-11-22T17:55:38+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:55:42+00:00 | crap-report | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0345b092da7ec86a` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-22T17:58:26+00:00 | mutation-changed | 1 | 159.88 | `python .migration/harness/tools/afs-mutation` | `428324c8c5a120c2` | afs-mutation: FAILED score=0.765 threshold=0.8 killed=39 survived=12 skipped=0 files=1 jobs=1 base=69441c3a713bf54fcd5c5 | gate=mutation score=0.765 threshold=0.8 killed=39 survived=12 files=1 base=69441c3a713bf54fcd5c5986d77603941a984e6d |
| 2026-11-22T17:59:21+00:00 | blank-deadline-red | 1 | 2.86 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_deadline_dialog_shows_parse_errors_without_updating_cargo` | `5f664baf34d3e321` | deadline = '', error = 'Choose an arrival deadline.' |  |
| 2026-11-22T17:59:41+00:00 | dialogs-targeted | 0 | 7.56 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `e719ef04f1779c8b` |  |  |
| 2026-11-22T18:02:51+00:00 | mutation-changed | 0 | 158.65 | `python .migration/harness/tools/afs-mutation` | `aa26c362dade515f` |  | gate=mutation score=0.846 threshold=0.8 killed=44 survived=8 files=1 base=69441c3a713bf54fcd5c5986d77603941a984e6d |
| 2026-11-22T18:03:51+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T18:03:55+00:00 | build-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T18:04:03+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T18:04:05+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-22T18:04:07+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-22T18:04:10+00:00 | idiom-ui | 0 | 0.72 | `python .migration/harness/tools/check_ui.py` | `1d5399c7b667e826` |  | gate=ui scope="templates changed since 69441c3a713bf54fcd5c5986d77603941a984e6d" templates=3 findings=0 |
| 2026-11-22T18:05:14+00:00 | behavior | 0 | 61.76 | `pytest -q` | `3d5fb4d1e7616323` |  |  |
| 2026-11-22T18:06:18+00:00 | crap-coverage | 0 | 61.73 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `5fe557c56ad5d039` |  |  |
| 2026-11-22T18:06:20+00:00 | crap-lizard | 0 | 0.16 | `lizard --csv src` | `db937aa173031402` | 16,3,86,6,16,"_origin_step@38-53@src/cargotracker/booking/interfaces/wizard/views.py","src/cargotracker/booking/interfac |  |
| 2026-11-22T18:06:25+00:00 | crap-lizard | 0 | 0.17 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T18:06:27+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0345b092da7ec86a` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-22T18:09:08+00:00 | mutation-changed | 0 | 159.79 | `python .migration/harness/tools/afs-mutation` | `aa26c362dade515f` |  | gate=mutation score=0.846 threshold=0.8 killed=44 survived=8 files=1 base=69441c3a713bf54fcd5c5986d77603941a984e6d |
