# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T15:29:13+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:30:16+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-16T15:31:59+00:00 | export-red | 1 | 2.44 | `pytest -q --no-cov tests/data_migration/test_export.py` | `e269e8c224e8e2c2` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-16T15:32:35+00:00 | export-tests | 1 | 0.94 | `pytest -q --no-cov tests/data_migration/test_export.py` | `0ef1c046b62569e1` | assert {path.name for path in output.glob('*.csv')} == { |  |
| 2026-11-16T15:32:50+00:00 | export-tests | 0 | 0.81 | `pytest -q --no-cov tests/data_migration/test_export.py` | `4a07fee0cbfe63fb` |  |  |
| 2026-11-16T15:33:34+00:00 | build | 0 | 0.34 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-16T15:33:38+00:00 | idiom | 0 | 0.04 | `bash -c 'ruff check && ruff format --check'` | `10aeae5796307327` |  |  |
| 2026-11-16T15:34:20+00:00 | behavior | 0 | 38.35 | `pytest -q` | `2ed35844121281bb` |  |  |
| 2026-11-16T15:34:59+00:00 | crap | 0 | 35.07 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `8468d5286044dae1` |  | gate=crap max=26.0 threshold=30 over=0 methods=181 |
| 2026-11-16T15:35:41+00:00 | regression | 0 | 36.15 | `pytest -q` | `1df03be7f8ba3a65` |  |  |
| 2026-11-16T15:35:57+00:00 | mutation-changed | 2 | 6.83 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `35aafee2343c9d86` | afs-mutation: mutmut failed on src/cargotracker/data_migration/exporter.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=2 files=2 base=origin/main |
| 2026-11-16T15:37:27+00:00 | export-tests | 0 | 0.85 | `pytest -q --no-cov tests/data_migration/test_export.py` | `71072fac3893e064` |  |  |
