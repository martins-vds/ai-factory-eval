# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T15:29:13+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:30:16+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-16T15:31:59+00:00 | export-red | 1 | 2.44 | `pytest -q --no-cov tests/data_migration/test_export.py` | `e269e8c224e8e2c2` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-16T15:32:35+00:00 | export-tests | 1 | 0.94 | `pytest -q --no-cov tests/data_migration/test_export.py` | `0ef1c046b62569e1` | assert {path.name for path in output.glob('*.csv')} == { |  |
| 2026-11-16T15:32:50+00:00 | export-tests | 0 | 0.81 | `pytest -q --no-cov tests/data_migration/test_export.py` | `4a07fee0cbfe63fb` |  |  |
