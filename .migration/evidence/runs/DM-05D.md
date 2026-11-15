# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T05:46:10+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T05:47:53+00:00 | snapshot-check | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-15T05:49:14+00:00 | export-tests-red | 1 | 3.57 | `pytest -q tests/data_migration/test_export.py` | `96274bc1eb7d29c5` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-15T05:49:57+00:00 | export-tests-green | 1 | 1.24 | `pytest -q tests/data_migration/test_export.py` | `0a36ff088aaeb6af` | assert { |  |
| 2026-11-15T05:50:07+00:00 | export-tests-green | 0 | 1.19 | `pytest -q tests/data_migration/test_export.py` | `62f575628765ad31` |  |  |
| 2026-11-15T05:51:05+00:00 | build | 0 | 0.29 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-15T05:51:09+00:00 | idiom | 1 | 0.03 | `bash -c 'ruff check && ruff format --check'` | `f3e1bc5a39efa090` |  |  |
| 2026-11-15T05:51:18+00:00 | idiom-rerun | 0 | 0.02 | `bash -c 'ruff check && ruff format --check'` | `178f4aac2b404dcb` |  |  |
| 2026-11-15T05:51:49+00:00 | behavior | 0 | 27.25 | `pytest -q` | `b5f39350bedaf2df` |  |  |
| 2026-11-15T05:52:23+00:00 | data-load | 1 | 0.28 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot --mapping .migration/data/mapping.yaml` | `39d84694036a43bc` | Traceback (most recent call last): |  |
| 2026-11-15T05:52:35+00:00 | target-migrate | 0 | 0.29 | `python manage.py migrate --noinput` | `56d728c244009843` |  |  |
| 2026-11-15T05:52:40+00:00 | data-load-rerun | 0 | 0.26 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot --mapping .migration/data/mapping.yaml` | `102e06696c233e34` |  |  |
| 2026-11-15T05:52:44+00:00 | data-export | 0 | 0.27 | `python manage.py export_data_snapshot --mapping .migration/data/mapping.yaml --out .migration/data/target-export` | `ba754ea10ff616fb` |  |  |
| 2026-11-15T05:52:49+00:00 | data-reconcile | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py reconcile --snapshot .migration/data/snapshot --target .migration/data/target-export --mapping .migration/data/mapping.yaml` | `0e5f155ede36068f` |  | gate=data-reconcile tables=6 rows=54 mismatched_tables=0 |
