# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-07T23:57:51+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-08T00:03:44+00:00 | dialogs-red | 2 | 1.95 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `87f1c6c7331d4445` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-08T00:04:46+00:00 | dialogs-green | 0 | 4.7 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `eff1b3de54d65623` |  |  |
| 2026-11-08T00:05:07+00:00 | bk05e-dashboard | 0 | 2.96 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `51dda580d2918aa0` |  |  |
| 2026-11-08T00:05:17+00:00 | idiom-ruff-check | 1 | 0.03 | `ruff check` | `a4ee59aa5ad2ed9a` | Found 1 error. |  |
| 2026-11-08T00:05:25+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-08T00:05:28+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `6aa724f0ec9c00d7` | 139 \|     assert updated.route_specification.destination == destination |  |
| 2026-11-08T00:05:38+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `c3ac60a207092b7f` |  |  |
| 2026-11-08T00:05:43+00:00 | build-compileall | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-08T00:05:46+00:00 | build-django-check | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-08T00:06:55+00:00 | tests | 0 | 64.21 | `pytest -q` | `19dfdd40492a0740` |  |  |
| 2026-11-08T00:08:24+00:00 | crap-pytest-cov | 0 | 61.14 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `0ff442a84f866c12` |  |  |
| 2026-11-08T00:08:27+00:00 | crap-lizard | 0 | 0.18 | `lizard --csv src` | `e2e1b0f77fba4a29` | 16,3,86,6,16,"_origin_step@38-53@src/cargotracker/booking/interfaces/wizard/views.py","src/cargotracker/booking/interfac |  |
| 2026-11-08T00:08:31+00:00 | crap-report | 1 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `1f315dff0c7b9238` |  |  |
| 2026-11-08T00:08:39+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-08T00:08:43+00:00 | crap-report | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `6ef01a8cb22fc870` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-08T00:08:50+00:00 | mutation-changed | 0 | 0.08 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-08T00:11:51+00:00 | mutation-changed | 1 | 134.69 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `7bd0ffa81156819e` | afs-mutation: FAILED score=0.691 threshold=0.8 killed=38 survived=17 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.691 threshold=0.8 killed=38 survived=17 files=1 base=origin/main |
| 2026-11-08T00:13:00+00:00 | dialogs-strengthened | 1 | 6.46 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `71894037e52b0aa6` | assert response.status_code == 404 |  |
| 2026-11-08T00:13:17+00:00 | dialogs-strengthened | 0 | 6.37 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `4c6aa90ff7519a34` |  |  |
| 2026-11-08T00:13:45+00:00 | dialogs-strengthened | 0 | 6.07 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `e2c340a19522d78a` |  |  |
| 2026-11-08T00:13:50+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-08T00:13:54+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `c3ac60a207092b7f` |  |  |
| 2026-11-08T00:16:43+00:00 | mutation-changed | 0 | 139.88 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `c97ad74d6bf2528b` |  | gate=mutation score=0.889 threshold=0.8 killed=48 survived=6 files=1 base=origin/main |
| 2026-11-08T00:18:22+00:00 | build-compileall | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-08T00:18:26+00:00 | build-django-check | 0 | 0.37 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-08T00:19:32+00:00 | tests | 0 | 62.64 | `pytest -q` | `8e2f81a9b0df7460` |  |  |
| 2026-11-08T00:20:38+00:00 | crap-pytest-cov | 0 | 61.03 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `e7901004ad0536ec` |  |  |
| 2026-11-08T00:20:43+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-08T00:20:47+00:00 | crap-report | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `513dbb0e36759c04` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-08T00:21:24+00:00 | accessible-dialog-red | 1 | 2.33 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_exposes_destination_and_deadline_dialogs` | `cb4e272f5d2b1495` | assert response.status_code == 200 |  |
| 2026-11-08T00:21:40+00:00 | accessible-dialog-green | 0 | 5.93 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `3f90d3c6bd454853` |  |  |
| 2026-11-08T00:21:52+00:00 | build-compileall | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-08T00:21:57+00:00 | build-django-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-08T00:22:02+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-08T00:22:06+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `c3ac60a207092b7f` |  |  |
| 2026-11-08T00:23:14+00:00 | tests | 0 | 62.58 | `pytest -q` | `a8f62c5b9797c245` |  |  |
| 2026-11-08T00:24:20+00:00 | crap-pytest-cov | 0 | 60.39 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `5efb9ccabe55cd8f` |  |  |
| 2026-11-08T00:24:24+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-08T00:24:30+00:00 | crap-report | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `513dbb0e36759c04` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-08T00:26:54+00:00 | mutation-changed | 0 | 139.12 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `c97ad74d6bf2528b` |  | gate=mutation score=0.889 threshold=0.8 killed=48 survived=6 files=1 base=origin/main |
| 2026-11-08T00:33:53+00:00 | restored-dashboard-scope | 0 | 7.12 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `fa17fd845c748e59` |  |  |
| 2026-11-08T00:35:07+00:00 | tests | 0 | 62.88 | `pytest -q` | `3cef3b8b6572c8e4` |  |  |
| 2026-11-17T16:25:51+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T16:29:47+00:00 | verifier-focused | 0 | 11.14 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `e88ab7b4902ba1b9` |  |  |
| 2026-11-17T16:31:50+00:00 | verifier-focused-final | 0 | 10.7 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py tests/booking/application/test_specification.py` | `00a753a2b09cf9fe` |  |  |
| 2026-11-17T16:32:29+00:00 | verifier-focused-final2 | 0 | 10.49 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py tests/booking/application/test_specification.py` | `6e6f6ecca30e2d5f` |  |  |
| 2026-11-17T16:36:29+00:00 | verifier-ui-errors | 1 | 0.46 | `python .migration/harness/tools/check_ui.py` | `ea2cae16af50f65a` | templates/booking/dashboard/not_routed_table.html:32: sends an htmx request ('hx-get'), but nothing handles error respon | gate=ui scope="templates changed since 79b524dae17ee2c968284e024737689c788695d0" templates=3 findings=3 |
| 2026-11-17T16:37:20+00:00 | verifier-build-compileall | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T16:37:29+00:00 | verifier-build-django-check | 0 | 0.39 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-17T16:38:40+00:00 | verifier-behavior | 0 | 67.84 | `pytest -q` | `f4d28e89b216c9b3` |  |  |
| 2026-11-17T16:38:45+00:00 | verifier-idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T16:38:48+00:00 | verifier-idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-17T16:38:52+00:00 | verifier-idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-17T16:40:07+00:00 | verifier-crap-coverage | 0 | 64.33 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `fe5802d7ff32d6f0` |  |  |
| 2026-11-17T16:40:11+00:00 | verifier-crap-lizard | 0 | 0.17 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T16:40:14+00:00 | verifier-crap-report | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `42b637de9cb6ebca` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-17T16:43:08+00:00 | verifier-mutation-changed | 0 | 167.1 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `b0a3022fd8b8d310` |  | gate=mutation score=0.907 threshold=0.8 killed=49 survived=5 files=1 base=origin/main |
| 2026-11-17T16:44:42+00:00 | verifier-regression | 0 | 64.94 | `pytest -q` | `b1664591a32f4c7b` |  |  |
