# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T00:43:59+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:44:37+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-23T00:46:05+00:00 | export-tests-red | 1 | 3.91 | `pytest -q tests/data_migration/test_export.py` | `82a3261b38114d1e` | E               KeyError: 'export_data_snapshot' |  |
