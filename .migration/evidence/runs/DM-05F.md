# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T04:11:16+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T04:12:46+00:00 | data-snapshot | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-15T04:15:06+00:00 | invariant-tests | 0 | 4.8 | `pytest -q tests/data_migration/test_invariants.py` | `55107bafcfbdb7c1` |  |  |
| 2026-11-15T04:15:46+00:00 | build | 0 | 0.43 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-15T04:16:41+00:00 | behavior | 0 | 50.5 | `pytest -q` | `a2efcdd3dbdf3585` |  |  |
| 2026-11-15T04:16:45+00:00 | idiom | 1 | 0.05 | `bash -c 'ruff check && ruff format --check'` | `69cd0424cf82e6a9` |  |  |
| 2026-11-15T04:16:55+00:00 | idiom | 0 | 0.03 | `bash -c 'ruff check && ruff format --check'` | `03298b321feb6bc6` |  |  |
| 2026-11-15T04:17:47+00:00 | crap | 0 | 47.76 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `d340655da8928e9f` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-15T05:02:03+00:00 | mutation-changed | 2 | 2652.86 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `d8faad82a4a7562b` | afs-mutation: mutmut failed on src/cargotracker/data_migration/loader.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=6 files=75 base=origin/main |
