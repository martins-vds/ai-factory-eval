# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:36:54+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:40:10+00:00 | dialogs-red | 2 | 2.73 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c901868299d894a6` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T13:41:19+00:00 | dialogs-targeted | 1 | 4.45 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c45d0dc774bf7716` | E       IndexError: list index out of range |  |
| 2026-11-18T13:41:34+00:00 | dialogs-targeted | 2 | 1.05 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `eb25dcfd79055457` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-18T13:41:45+00:00 | dialogs-targeted | 1 | 4.37 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `31b11f0c7d2d9c26` | assert response.status_code == 200 |  |
| 2026-11-18T13:42:20+00:00 | dialogs-targeted | 0 | 4.37 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `3539f262acf29f0e` |  |  |
| 2026-11-18T13:43:00+00:00 | dialogs-targeted | 0 | 4.86 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2813771d2a0d963d` |  |  |
| 2026-11-18T13:44:53+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:44:56+00:00 | build-check | 0 | 0.37 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T13:45:00+00:00 | idiom-ruff | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T13:45:03+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `5d148696a234e5f2` | 173 \|     assert cargo is not None |  |
| 2026-11-18T13:45:11+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-18T13:45:15+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T13:45:19+00:00 | idiom-ui | 0 | 0.53 | `python .migration/harness/tools/check_ui.py` | `f79293a81a83b203` |  | gate=ui scope="templates changed since 71d913629b5bbcb385c7a0d592ede9d1cd1caaec" templates=4 findings=0 |
| 2026-11-18T13:46:36+00:00 | regression | 0 | 62.41 | `pytest -q` | `18e0479cdc0d5b27` |  |  |
| 2026-11-18T13:47:39+00:00 | crap-pytest | 0 | 59.66 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `599f8eceb7d97c86` |  |  |
| 2026-11-18T13:47:44+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:47:47+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0cea1cdfeb73461b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-18T13:53:52+00:00 | mutation-changed | 1 | 147.33 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `b8c70daa79653382` | afs-mutation: FAILED score=0.722 threshold=0.8 killed=39 survived=15 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.722 threshold=0.8 killed=39 survived=15 files=1 base=origin/main |
| 2026-11-18T13:55:43+00:00 | dialogs-targeted | 0 | 5.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `846032b0b45931c5` |  |  |
