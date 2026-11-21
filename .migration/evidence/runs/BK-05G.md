# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T13:08:29+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:11:39+00:00 | dialogs-red | 2 | 2.99 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c901868299d894a6` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-21T13:12:28+00:00 | dialogs-green | 1 | 4.97 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `1341e779f96a59fa` | assert first_response.status_code == 200 |  |
| 2026-11-21T13:12:44+00:00 | dialogs-green-2 | 0 | 4.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `cd0087a16290275a` |  |  |
| 2026-11-21T13:12:56+00:00 | dashboard-regression | 0 | 2.9 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `708feca03f39820e` |  |  |
| 2026-11-21T13:13:24+00:00 | dialogs-final | 0 | 5.24 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `566e29345cd83114` |  |  |
| 2026-11-21T13:13:29+00:00 | dashboard-regression-final | 0 | 2.83 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `2f4844acf2808bec` |  |  |
| 2026-11-21T13:15:11+00:00 | idiom-ruff-check | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:15:13+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `aef39158235b96b0` |  |  |
| 2026-11-21T13:15:21+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T13:15:24+00:00 | build-compileall | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:15:26+00:00 | build-django-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T13:15:29+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T13:15:32+00:00 | idiom-ui | 0 | 0.62 | `python .migration/harness/tools/check_ui.py` | `4be95899e1f4062a` |  | gate=ui scope="templates changed since 256fbe36bcab1dc38117715631d54b7d8cefc2c0" templates=4 findings=0 |
| 2026-11-21T13:16:38+00:00 | behavior-suite | 0 | 60.83 | `pytest -q` | `f8d52d06a5ffc8ce` |  |  |
| 2026-11-21T13:17:53+00:00 | crap-coverage | 0 | 72.28 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `75bb1753df5393f7` |  |  |
| 2026-11-21T13:17:56+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:17:59+00:00 | crap-report | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `84bc4e12796d52be` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-21T13:21:43+00:00 | mutation-changed | 1 | 174.6 | `python .migration/harness/tools/afs-mutation` | `d49cad6c88521064` | afs-mutation: FAILED score=0.783 threshold=0.8 killed=47 survived=13 skipped=0 files=1 jobs=1 base=256fbe36bcab1dc381177 | gate=mutation score=0.783 threshold=0.8 killed=47 survived=13 files=1 base=256fbe36bcab1dc38117715631d54b7d8cefc2c0 |
| 2026-11-21T13:22:40+00:00 | dialogs-after-review | 0 | 6.3 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `4019613c86033dbe` |  |  |
| 2026-11-21T13:25:09+00:00 | mutation-changed-final | 0 | 145.49 | `python .migration/harness/tools/afs-mutation` | `f8db28256c6add14` |  | gate=mutation score=0.904 threshold=0.8 killed=47 survived=5 files=1 base=256fbe36bcab1dc38117715631d54b7d8cefc2c0 |
| 2026-11-21T13:25:22+00:00 | final-build-compileall | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:25:25+00:00 | final-build-django-check | 0 | 0.37 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T13:25:28+00:00 | final-idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:25:31+00:00 | final-idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T13:25:34+00:00 | final-idiom-layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T13:25:37+00:00 | final-idiom-ui | 0 | 0.64 | `python .migration/harness/tools/check_ui.py` | `4be95899e1f4062a` |  | gate=ui scope="templates changed since 256fbe36bcab1dc38117715631d54b7d8cefc2c0" templates=4 findings=0 |
| 2026-11-21T13:26:45+00:00 | final-behavior-suite | 0 | 64.13 | `pytest -q` | `f949dfd1f08da394` |  |  |
| 2026-11-21T13:27:49+00:00 | final-crap-coverage | 0 | 61.76 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `3a30ebf26e1af303` |  |  |
| 2026-11-21T13:27:52+00:00 | final-crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:27:55+00:00 | final-crap-report | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0cea1cdfeb73461b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-21T13:29:09+00:00 | regression-suite | 0 | 61.98 | `pytest -q` | `ecf64fb723ed4a93` |  |  |
| 2026-11-21T13:32:46+00:00 | post-codeql-build-compileall | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:32:48+00:00 | post-codeql-build-django-check | 0 | 0.37 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T13:32:52+00:00 | post-codeql-idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:32:55+00:00 | post-codeql-idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T13:32:59+00:00 | post-codeql-idiom-layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T13:33:03+00:00 | post-codeql-idiom-ui | 0 | 0.65 | `python .migration/harness/tools/check_ui.py` | `4be95899e1f4062a` |  | gate=ui scope="templates changed since 256fbe36bcab1dc38117715631d54b7d8cefc2c0" templates=4 findings=0 |
| 2026-11-21T13:34:08+00:00 | post-codeql-behavior-suite | 0 | 62.22 | `pytest -q` | `19527c1cf486f51d` |  |  |
| 2026-11-21T13:35:25+00:00 | post-codeql-crap-coverage | 0 | 74.07 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `e9436baa9e85248f` |  |  |
| 2026-11-21T13:35:28+00:00 | post-codeql-crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:35:31+00:00 | post-codeql-crap-report | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0cea1cdfeb73461b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-21T13:37:57+00:00 | post-codeql-mutation-changed | 0 | 142.37 | `python .migration/harness/tools/afs-mutation` | `f8db28256c6add14` |  | gate=mutation score=0.904 threshold=0.8 killed=47 survived=5 files=1 base=256fbe36bcab1dc38117715631d54b7d8cefc2c0 |
| 2026-11-21T13:39:04+00:00 | post-codeql-regression-suite | 0 | 63.24 | `pytest -q` | `cb3ca1931a3d4eb9` |  |  |
