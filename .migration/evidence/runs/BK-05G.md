# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T13:36:37+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:40:33+00:00 | red-destination-dialog | 2 | 0.78 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2237198fd9734b3c` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T13:44:31+00:00 | green-destination-initial | 0 | 1.25 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `38e13be45293b3a0` |  |  |
| 2026-11-18T13:44:47+00:00 | red-invalid-destination | 1 | 1.27 | `pytest -q tests/booking/interfaces/test_dialogs.py -k rejects_origin` | `c4d6d8a84c23ee02` | assert response.status_code == 200 |  |
| 2026-11-18T13:45:10+00:00 | green-destination-boundary | 0 | 1.48 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ae472916d0d50dc9` |  |  |
| 2026-11-18T13:46:06+00:00 | red-deadline-initial | 2 | 0.57 | `pytest -q tests/booking/interfaces/test_dialogs.py -k deadline_dialog` | `3280b595539d8d38` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T13:46:21+00:00 | green-deadline-initial | 2 | 0.54 | `pytest -q tests/booking/interfaces/test_dialogs.py -k deadline_dialog` | `2d400fe10c1aba72` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T13:46:29+00:00 | green-deadline-initial | 0 | 1.28 | `pytest -q tests/booking/interfaces/test_dialogs.py -k deadline_dialog` | `772d478cfb65248c` |  |  |
| 2026-11-18T13:46:40+00:00 | red-deadline-parse-error | 1 | 1.31 | `pytest -q tests/booking/interfaces/test_dialogs.py -k parse_error` | `4f5fb2d042b7759d` | assert cargo is not None |  |
| 2026-11-18T13:46:58+00:00 | red-deadline-success | 1 | 1.38 | `pytest -q tests/booking/interfaces/test_dialogs.py -k updates_deadline` | `f7d8842ef45cf804` | assert cargo is not None |  |
| 2026-11-18T13:47:18+00:00 | green-deadline-flows | 0 | 2.29 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8c6fecfc1b2d4cb4` |  |  |
| 2026-11-18T13:47:51+00:00 | stable-destination-options | 1 | 1.28 | `pytest -q tests/booking/interfaces/test_dialogs.py -k stable_across_renders` | `317464814fa5d506` | E       TypeError: create_destination_dialog_view() missing 1 required positional argument: 'list_shipping_locations' |  |
| 2026-11-18T13:48:00+00:00 | stable-destination-options | 0 | 1.27 | `pytest -q tests/booking/interfaces/test_dialogs.py -k stable_across_renders` | `4bdbdee06d197466` |  |  |
| 2026-11-18T13:48:17+00:00 | red-dialog-table-actions | 1 | 1.31 | `pytest -q tests/booking/interfaces/test_dialogs.py -k opens_destination` | `a1058d27d1976f2e` | assert response.status_code == 200 |  |
| 2026-11-18T13:48:38+00:00 | green-dialog-flows | 0 | 2.9 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `833d0e0e1598f02f` |  |  |
| 2026-11-18T13:48:44+00:00 | dashboard-regression | 0 | 1.61 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `7d4c2db06b269aea` |  |  |
| 2026-11-18T13:49:56+00:00 | ui-boundary-regression | 0 | 3.48 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `be6b35fc91699d3b` |  |  |
| 2026-11-18T13:49:59+00:00 | ui-template-check | 0 | 0.27 | `python .migration/harness/tools/check_ui.py` | `7c2daa377753628d` |  | gate=ui scope="templates changed since 0e7957db18c6fb70b7245b24e4a6ac8e854abe5f" templates=3 findings=0 |
| 2026-11-18T13:52:25+00:00 | focused-dialog-suite | 0 | 3.48 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `4201ab072cc558d0` |  |  |
| 2026-11-18T13:52:29+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `a41e36073d296c99` | Found 1 error. |  |
| 2026-11-18T13:52:35+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T13:52:39+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `57f66d94f77b3a7b` |  |  |
| 2026-11-18T13:52:54+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T13:53:57+00:00 | focused-dialog-tests | 1 | 3.23 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `d1505eba75da152e` | E       AssertionError: Regex pattern did not match. |  |
| 2026-11-18T13:54:05+00:00 | focused-dialog-tests | 0 | 3.27 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `bf52e4e51d0f2814` |  |  |
| 2026-11-18T13:55:50+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:55:50+00:00 | build-django-check | 0 | 0.21 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T13:55:54+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T13:55:54+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T13:55:54+00:00 | idiom-layers | 0 | 0.09 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T13:55:54+00:00 | idiom-ui | 0 | 0.27 | `python .migration/harness/tools/check_ui.py` | `0b2fb4bd5013f20c` |  | gate=ui scope="templates changed since 0e7957db18c6fb70b7245b24e4a6ac8e854abe5f" templates=4 findings=0 |
| 2026-11-18T13:56:29+00:00 | full-tests | 0 | 32.1 | `pytest -q` | `c0da0f03398460ff` |  |  |
| 2026-11-18T13:57:08+00:00 | crap-pytest | 0 | 32.91 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `1d44ac13729415ec` |  |  |
| 2026-11-18T13:57:08+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:57:08+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `30fa8e1a459b6241` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-18T13:58:38+00:00 | changed-mutation | 1 | 85.39 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `253271dc691504d1` | afs-mutation: FAILED score=0.679 threshold=0.8 killed=36 survived=17 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.679 threshold=0.8 killed=36 survived=17 files=1 base=origin/main |
| 2026-11-18T13:59:39+00:00 | focused-dialog-tests | 0 | 4.17 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0569c803c842924d` |  |  |
| 2026-11-18T14:01:11+00:00 | changed-mutation | 0 | 88.63 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `e57962d7d34c962b` |  | gate=mutation score=0.981 threshold=0.8 killed=52 survived=1 files=1 base=origin/main |
| 2026-11-18T14:02:16+00:00 | final-build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T14:02:16+00:00 | final-build-django-check | 0 | 0.21 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T14:02:16+00:00 | final-idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T14:02:16+00:00 | final-idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T14:02:17+00:00 | final-idiom-layers | 0 | 0.09 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T14:02:17+00:00 | final-idiom-ui | 0 | 0.28 | `python .migration/harness/tools/check_ui.py` | `0b2fb4bd5013f20c` |  | gate=ui scope="templates changed since 0e7957db18c6fb70b7245b24e4a6ac8e854abe5f" templates=4 findings=0 |
| 2026-11-18T14:02:54+00:00 | final-full-tests | 0 | 33.39 | `pytest -q` | `c7c5a68274058de3` |  |  |
| 2026-11-18T14:03:33+00:00 | final-crap-pytest | 0 | 33.81 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `8b717673a6be72f6` |  |  |
| 2026-11-18T14:03:33+00:00 | final-crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T14:03:33+00:00 | final-crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `6d739c2b1aec51ac` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-18T14:05:04+00:00 | final-changed-mutation | 0 | 88.31 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `e57962d7d34c962b` |  | gate=mutation score=0.981 threshold=0.8 killed=52 survived=1 files=1 base=origin/main |
| 2026-11-18T14:05:21+00:00 | final-migration-validation | 1 | 3.2 | `python .migration/harness/tools/validate.py .migration` | `33df92e3d08fee72` | 193 file(s) checked, 3 error(s) |  |
| 2026-11-18T14:05:32+00:00 | final-migration-validation | 0 | 3.21 | `python .migration/harness/tools/validate.py .migration` | `ef34805838431398` |  |  |
| 2026-11-18T15:42:57+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T15:47:12+00:00 | verifier-focused-tests | 0 | 6.55 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `70acccac6515761f` |  |  |
