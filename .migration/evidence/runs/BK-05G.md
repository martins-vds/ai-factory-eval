# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T12:50:51+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:53:54+00:00 | tests-red | 2 | 2.54 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ff2941dac61b6088` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T12:54:46+00:00 | dialogs-targeted | 1 | 6.9 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `a6b0390320c840a7` | assert locations == initial_locations |  |
| 2026-11-18T12:55:07+00:00 | dialogs-targeted | 1 | 6.56 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `ca4bb3ba4a0cb0cd` | assert locations == initial_locations |  |
| 2026-11-18T12:55:23+00:00 | dialogs-targeted | 0 | 6.42 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `a5692a78cfee1117` |  |  |
| 2026-11-18T12:55:50+00:00 | dialogs-targeted | 0 | 6.62 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `2ef850f287531bdb` |  |  |
| 2026-11-18T12:56:24+00:00 | dialogs-targeted | 1 | 6.64 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `3035f919e469ef4e` | /opt/hostedtoolcache/Python/3.13.18/x64/lib/python3.13/site-packages/django/core/handlers/exception.py:55: in inner |  |
| 2026-11-18T12:56:36+00:00 | dialogs-targeted | 0 | 6.85 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `b09713926ed0ac0a` |  |  |
| 2026-11-18T12:56:42+00:00 | build-compileall | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:56:42+00:00 | build-django-check | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T12:56:42+00:00 | idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:56:42+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `c82bdde39e998bc0` | 143 \|     assert 'New York' in content |  |
| 2026-11-18T12:56:51+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-18T12:56:55+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T12:56:56+00:00 | idiom-ui | 1 | 0.54 | `python .migration/harness/tools/check_ui.py` | `65e1f4087b1c7fe4` | templates/booking/dialogs/deadline.html:9: sends an htmx request ('hx-post'), but nothing handles error responses: htmx  | gate=ui scope="templates changed since 07c357cf95f91dfffaf2334a0675068b38745e1d" templates=2 findings=2 |
| 2026-11-18T12:57:22+00:00 | idiom-ui | 0 | 0.51 | `python .migration/harness/tools/check_ui.py` | `8be7bd64cfb1043a` |  | gate=ui scope="templates changed since 07c357cf95f91dfffaf2334a0675068b38745e1d" templates=2 findings=0 |
| 2026-11-18T13:00:11+00:00 | behavior | 0 | 62.11 | `pytest -q` | `33dcfa8e7280a699` |  |  |
| 2026-11-18T13:01:31+00:00 | crap-coverage | 0 | 72.15 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `fe8d0d25098230d5` |  |  |
| 2026-11-18T13:01:35+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:01:35+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `568138dadd34e9db` |  | gate=crap max=26.0 threshold=30 over=0 methods=207 |
| 2026-11-18T13:10:46+00:00 | mutation-changed | 1 | 546.9 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `f8c2c952c8c6f2a6` | afs-mutation: FAILED score=0.759 threshold=0.8 killed=60 survived=19 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.759 threshold=0.8 killed=60 survived=19 files=1 base=origin/main |
| 2026-11-18T13:11:44+00:00 | stale-dialog-red | 1 | 2.06 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_dialogs_return_not_found_for_unknown_cargo` | `e19e736f51a0f766` | assert response.status_code == 404 |  |
| 2026-11-18T13:12:11+00:00 | dialogs-targeted | 1 | 7.79 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `63903f57a8ff193c` | assert cargo_before is not None |  |
| 2026-11-18T13:13:11+00:00 | dialogs-targeted | 0 | 7.29 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `9b8e371e72d86dc2` |  |  |
| 2026-11-18T13:13:46+00:00 | dialogs-targeted | 0 | 7.76 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `73153a7f34b1e9e3` |  |  |
| 2026-11-18T13:15:03+00:00 | behavior | 0 | 61.78 | `pytest -q` | `f6a4e50954b2f4f7` |  |  |
| 2026-11-18T13:15:09+00:00 | build-compileall | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:15:09+00:00 | build-django-check | 0 | 0.37 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T13:15:09+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T13:15:09+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-18T13:15:09+00:00 | idiom-layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T13:15:10+00:00 | idiom-ui | 0 | 0.54 | `python .migration/harness/tools/check_ui.py` | `66b28d168bd5bf98` |  | gate=ui scope="templates changed since 07c357cf95f91dfffaf2334a0675068b38745e1d" templates=4 findings=0 |
| 2026-11-18T13:16:17+00:00 | crap-coverage | 0 | 62.37 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `4c99d99562c8641a` |  |  |
| 2026-11-18T13:16:17+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:16:17+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `568138dadd34e9db` |  | gate=crap max=26.0 threshold=30 over=0 methods=207 |
| 2026-11-18T13:25:00+00:00 | mutation-changed | 0 | 491.33 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `108a5fc02c75c6d3` |  | gate=mutation score=0.954 threshold=0.8 killed=83 survived=4 files=1 base=origin/main |
| 2026-11-18T13:29:32+00:00 | dialogs-targeted | 0 | 7.66 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `038e5c12b982dbf5` |  |  |
| 2026-11-18T14:17:16+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T14:19:40+00:00 | verifier-build-compileall | 0 | 0.1 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T14:19:45+00:00 | verifier-build-django-check | 0 | 1.23 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T14:19:48+00:00 | verifier-idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T14:19:51+00:00 | verifier-idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T14:19:54+00:00 | verifier-idiom-layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T14:19:57+00:00 | verifier-idiom-ui | 0 | 0.51 | `python .migration/harness/tools/check_ui.py` | `66b28d168bd5bf98` |  | gate=ui scope="templates changed since 07c357cf95f91dfffaf2334a0675068b38745e1d" templates=4 findings=0 |
| 2026-11-18T14:21:07+00:00 | verifier-behavior | 0 | 65.98 | `pytest -q` | `0309a319f05d75b1` |  |  |
| 2026-11-18T14:22:26+00:00 | verifier-crap-coverage | 0 | 63.66 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `a2327969bb74adcf` |  |  |
| 2026-11-18T14:22:29+00:00 | verifier-crap-lizard | 0 | 0.18 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T14:22:32+00:00 | verifier-crap-score | 0 | 0.06 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `568138dadd34e9db` |  | gate=crap max=26.0 threshold=30 over=0 methods=207 |
| 2026-11-18T14:31:10+00:00 | verifier-mutation-changed | 0 | 513.72 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `108a5fc02c75c6d3` |  | gate=mutation score=0.954 threshold=0.8 killed=83 survived=4 files=1 base=origin/main |
| 2026-11-18T14:31:40+00:00 | verifier-usecase-tests | 0 | 2.16 | `pytest -q tests/booking/application/test_specification.py` | `1506dfd15c53159c` |  |  |
| 2026-11-18T14:31:44+00:00 | verifier-final-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T14:31:48+00:00 | verifier-final-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T14:33:01+00:00 | verifier-behavior-final | 0 | 65.03 | `pytest -q` | `42ad7bdb67cac159` |  |  |
| 2026-11-18T14:34:12+00:00 | verifier-regression | 0 | 61.87 | `pytest -q` | `05658d7defac3ebb` |  |  |
| 2026-11-18T14:35:21+00:00 | verifier-final-crap-coverage | 0 | 65.81 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `bb236b849bab7a03` |  |  |
| 2026-11-18T14:35:25+00:00 | verifier-final-crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T14:35:29+00:00 | verifier-final-crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `568138dadd34e9db` |  | gate=crap max=26.0 threshold=30 over=0 methods=207 |
