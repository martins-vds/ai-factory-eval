# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T06:09:21+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T06:12:35+00:00 | export-red | 1 | 1.34 | `pytest -q tests/data_migration/test_export.py` | `0ff60ee5e1e93c6e` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-15T06:12:58+00:00 | export-tests | 0 | 1.15 | `pytest -q tests/data_migration/test_export.py` | `791313e37fd7699e` |  |  |
| 2026-11-15T06:13:16+00:00 | snapshot-check | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-15T06:13:22+00:00 | build | 0 | 0.27 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-15T06:13:54+00:00 | tests | 0 | 27.45 | `pytest -q` | `b754ef8813f0d696` |  |  |
| 2026-11-15T06:13:58+00:00 | idiom | 0 | 0.03 | `bash -c 'ruff check && ruff format --check'` | `178f4aac2b404dcb` |  |  |
| 2026-11-15T06:14:28+00:00 | crap | 0 | 25.59 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `dc505b13cbf4ecfd` |  | gate=crap max=26.0 threshold=30 over=0 methods=185 |
| 2026-11-15T06:45:35+00:00 | mutation-changed | 2 | 1862.94 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `09af2464c42c8092` | afs-mutation: mutmut failed on src/cargotracker/data_migration/loader.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=2 files=75 base=origin/main |
