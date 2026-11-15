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
