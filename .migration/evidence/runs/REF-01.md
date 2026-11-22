# Run journal: REF-01

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T04:20:14+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:21:14+00:00 | schema-contract-red | 2 | 1.71 | `pytest -q tests/data_migration/test_export.py -k 'model_index_excludes or interprets_naive'` | `4c598d19a762a646` | _____________ ERROR collecting tests/data_migration/test_export.py _____________ |  |
| 2026-11-22T04:21:33+00:00 | export-tests | 0 | 1.52 | `pytest -q tests/data_migration/test_export.py` | `a5b90414d6a07cbc` |  |  |
| 2026-11-22T04:22:09+00:00 | build | 0 | 0.3 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-22T04:22:55+00:00 | behavior | 0 | 44.11 | `pytest -q` | `4438357178efcc7b` |  |  |
| 2026-11-22T04:22:58+00:00 | idiom | 1 | 0.02 | `bash -c 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `8bf2f5b75f465631` | Found 1 error. |  |
| 2026-11-22T04:23:06+00:00 | export-tests-final | 0 | 1.3 | `pytest -q tests/data_migration/test_export.py` | `3730d290bb3a084d` |  |  |
| 2026-11-22T04:23:08+00:00 | idiom | 0 | 0.52 | `bash -c 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `8f72fd90c6cc107d` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=ui scope="templates changed since a5a5f4c3c4a4bb9dd49b2ac13729bd4d9ba31ecf" templates=0 findings=0 |
| 2026-11-22T04:23:51+00:00 | crap | 0 | 39.81 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `89e9a9a6ed092234` |  | gate=crap max=26.0 threshold=30 over=0 methods=213 |
| 2026-11-22T04:25:00+00:00 | mutation-changed | 0 | 53.1 | `python .migration/harness/tools/afs-mutation` | `d2e8272ff63c68aa` |  | gate=mutation score=0.978 threshold=0.8 killed=90 survived=2 files=2 base=a5a5f4c3c4a4bb9dd49b2ac13729bd4d9ba31ecf |
| 2026-11-22T04:25:46+00:00 | regression | 0 | 39.7 | `pytest -q` | `99e4f1c75d454699` |  |  |
| 2026-11-22T04:29:55+00:00 | build-final | 0 | 0.29 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-22T04:30:40+00:00 | behavior-final | 0 | 42.34 | `pytest -q` | `9198577e6cacaf03` |  |  |
