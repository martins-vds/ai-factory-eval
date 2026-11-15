# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T04:10:10+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T04:10:36+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-15T04:12:26+00:00 | export-red | 1 | 3.12 | `pytest -q tests/data_migration/test_export.py` | `0ac8be75739d31e1` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-15T04:12:52+00:00 | export-test | 1 | 1.25 | `pytest -q tests/data_migration/test_export.py` | `bbea4f3d70b781db` | assert {path.stem for path in output.glob('*.csv')} == { |  |
| 2026-11-15T04:13:03+00:00 | export-test | 0 | 1.24 | `pytest -q tests/data_migration/test_export.py` | `2082fa6110502427` |  |  |
| 2026-11-15T04:13:31+00:00 | export-test-order | 0 | 1.33 | `pytest -q tests/data_migration/test_export.py` | `f34bbeaad9b69d77` |  |  |
| 2026-11-15T04:13:50+00:00 | compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T04:13:54+00:00 | django-check | 0 | 0.28 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T04:13:58+00:00 | ruff-check | 1 | 0.02 | `ruff check` | `0ea641a83ad91821` | Found 1 error. |  |
| 2026-11-15T04:14:08+00:00 | ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T04:14:11+00:00 | ruff-format | 0 | 0.02 | `ruff format --check` | `c7a0bcb17dd5241a` |  |  |
| 2026-11-15T04:14:50+00:00 | tests | 0 | 35.53 | `pytest -q` | `ed17a941baa2622f` |  |  |
| 2026-11-15T04:15:30+00:00 | crap-coverage | 0 | 35.64 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `1c4b4b32cd420c90` |  |  |
| 2026-11-15T04:15:34+00:00 | crap-lizard | 0 | 0.09 | `lizard --csv src '>' .migration/runs/lizard.csv` | `132617c68251425c` |  |  |
| 2026-11-15T04:15:47+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T04:15:51+00:00 | crap | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `f8d2eb5d60f17a2e` |  | gate=crap max=26.0 threshold=30 over=0 methods=184 |
| 2026-11-15T04:54:16+00:00 | mutation-changed | 2 | 2301.01 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `58884ecf7dc44466` | afs-mutation: mutmut failed on src/cargotracker/data_migration/loader.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=1 files=77 base=origin/main |
| 2026-11-15T04:55:08+00:00 | export-test-self-contained | 0 | 1.27 | `pytest -q tests/data_migration/test_export.py` | `e208fe9d2cdfeb65` |  |  |
| 2026-11-15T04:55:19+00:00 | ruff-check | 1 | 0.21 | `ruff check` | `34a02566d264d826` | Found 1 error. |  |
| 2026-11-15T04:55:26+00:00 | ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T04:55:30+00:00 | ruff-format | 0 | 0.01 | `ruff format --check` | `c7a0bcb17dd5241a` |  |  |
| 2026-11-15T04:56:10+00:00 | tests | 0 | 36.41 | `pytest -q` | `6a47266ad186cdbb` |  |  |
