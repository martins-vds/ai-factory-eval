# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T13:55:05+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:59:57+00:00 | dialog-red-01 | 2 | 6.57 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `393c99da5d916289` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-19T14:01:13+00:00 | dialog-green-01 | 1 | 2.39 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0538ccf330c39542` | assert cargo is not None |  |
| 2026-11-19T14:01:25+00:00 | dialog-green-01 | 0 | 2.15 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `120e924bac659ca9` |  |  |
| 2026-11-19T14:02:42+00:00 | dialogs-targeted | 0 | 7.13 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `60f93a3101d33494` |  |  |
| 2026-11-19T14:05:55+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:05:58+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T14:06:07+00:00 | behavior | 0 | 5.8 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `2d920ef238ac680d` |  |  |
| 2026-11-19T14:06:11+00:00 | idiom-ruff | 1 | 0.03 | `ruff check` | `b537121633229af1` | Found 1 error. |  |
| 2026-11-19T14:06:20+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T14:06:23+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `26c55f7f69d7671f` | 196 \|     assert updated_cargo.route_specification.destination == cargo.route_specification.destination |  |
| 2026-11-19T14:06:32+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T14:06:36+00:00 | idiom-layers | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T14:06:40+00:00 | idiom-ui | 0 | 0.43 | `python .migration/harness/tools/check_ui.py` | `8c1dcbe38923e2c6` |  | gate=ui scope="templates changed since c9fcae5717caa37e32152bd9ec8e3755288a47bb" templates=7 findings=0 |
| 2026-11-19T14:07:48+00:00 | crap-coverage | 0 | 58.24 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `6a3284476d38a22e` |  |  |
| 2026-11-19T14:07:51+00:00 | crap-lizard | 0 | 0.13 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:07:56+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `7363e3b7e7cc5669` |  | gate=crap max=26.0 threshold=30 over=0 methods=208 |
| 2026-11-19T14:11:21+00:00 | mutation-changed | 1 | 199.83 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `019f41496692bf5b` | afs-mutation: FAILED score=0.679 threshold=0.8 killed=55 survived=26 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.679 threshold=0.8 killed=55 survived=26 files=1 base=origin/main |
| 2026-11-19T14:12:53+00:00 | behavior-hardening | 0 | 8.16 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `014406270d9a9aee` |  |  |
| 2026-11-19T14:13:04+00:00 | idiom-ruff | 1 | 0.01 | `ruff check` | `e29a831dbacdf7f7` | 96 \|     assert f'action="{DESTINATION_PATH}"' in destination_response.content.decode() |  |
| 2026-11-19T14:13:13+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T14:13:13+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T14:13:13+00:00 | idiom-layers | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T14:13:14+00:00 | idiom-ui | 0 | 0.44 | `python .migration/harness/tools/check_ui.py` | `8c1dcbe38923e2c6` |  | gate=ui scope="templates changed since c9fcae5717caa37e32152bd9ec8e3755288a47bb" templates=7 findings=0 |
| 2026-11-19T14:17:15+00:00 | mutation-changed | 0 | 237.85 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `4c7e0ff43ef98062` |  | gate=mutation score=0.938 threshold=0.8 killed=75 survived=5 files=1 base=origin/main |
| 2026-11-19T14:17:56+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:18:01+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T14:19:04+00:00 | crap-coverage | 0 | 59.73 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `880244583e704228` |  |  |
| 2026-11-19T14:19:09+00:00 | crap-lizard | 0 | 0.13 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:19:09+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `4c8190a594ae27cc` |  | gate=crap max=26.0 threshold=30 over=0 methods=208 |
| 2026-11-19T14:20:12+00:00 | regression | 0 | 57.54 | `pytest -q` | `d535658b091ceb0c` |  |  |
