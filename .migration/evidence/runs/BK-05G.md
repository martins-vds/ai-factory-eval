# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:47:51+00:00 | setup-probe | 0 | 0.01 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:51:12+00:00 | dialogs-red | 2 | 3.55 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `92eea115bd4dfeca` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-19T13:52:15+00:00 | destination-green | 1 | 2.25 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `18bd88a2c447df1f` | assert locations == original_locations |  |
| 2026-11-19T13:52:23+00:00 | destination-green | 0 | 2.03 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `73e52fbff0780f58` |  |  |
| 2026-11-19T13:53:06+00:00 | integration-red | 1 | 3.11 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `13c68dd23bdf9620` | assert cargo is not None |  |
| 2026-11-19T13:53:27+00:00 | dialogs-and-dashboard | 0 | 4.02 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `84ef7238ff42c4c6` |  |  |
| 2026-11-19T13:53:56+00:00 | dialogs-and-dashboard | 0 | 3.79 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `ac3d68313e6a4528` |  |  |
| 2026-11-19T13:54:59+00:00 | dialogs-http | 0 | 4.4 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `81fe7e4b69df0f53` |  |  |
| 2026-11-19T13:56:41+00:00 | build-compileall | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:56:45+00:00 | build-django-check | 0 | 0.32 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T13:56:49+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T13:56:52+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `943dac169143c322` | 53  \|         assert response.status_code == 200 |  |
| 2026-11-19T13:57:05+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-19T13:57:09+00:00 | idiom-layers | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T13:57:12+00:00 | idiom-ui | 0 | 0.41 | `python .migration/harness/tools/check_ui.py` | `48b90a9b847373be` |  | gate=ui scope="templates changed since e08aa994eab0967797d617f883734c0c8d874cd7" templates=3 findings=0 |
| 2026-11-19T13:58:05+00:00 | behavior | 0 | 49.49 | `pytest -q` | `b4cba455a58877df` |  |  |
| 2026-11-19T13:58:56+00:00 | crap-coverage | 0 | 44.57 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `700904189d15da11` |  |  |
| 2026-11-19T13:58:59+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:59:02+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `11e7e6b1a41eff5d` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-19T14:00:50+00:00 | mutation-changed | 1 | 104.24 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `b5f43b8f7e7f8b49` | afs-mutation: FAILED score=0.778 threshold=0.8 killed=49 survived=14 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.778 threshold=0.8 killed=49 survived=14 files=1 base=origin/main |
| 2026-11-19T14:02:26+00:00 | mutation-followup-tests | 0 | 4.73 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `fd2551a5a6074963` |  |  |
| 2026-11-19T14:02:46+00:00 | idiom-format-followup | 0 | 0.01 | `ruff format --check` | `3accebe6ea89f2c7` |  |  |
| 2026-11-19T14:03:26+00:00 | mutation-followup-tests | 0 | 4.65 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `5a66c1626b1dd64f` |  |  |
| 2026-11-19T14:05:44+00:00 | mutation-changed | 0 | 100.41 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `d9981ab6bba0dcc3` |  | gate=mutation score=0.952 threshold=0.8 killed=59 survived=3 files=1 base=origin/main |
| 2026-11-19T14:10:13+00:00 | scope-cleanup | 0 | 3.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ad4dc636c010c6b7` |  |  |
