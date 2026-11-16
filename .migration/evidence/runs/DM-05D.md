# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T17:28:58+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:29:47+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-16T17:32:01+00:00 | export-tests-red | 1 | 2.36 | `pytest -q tests/data_migration/test_export.py` | `dc7d37cd86b81962` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-16T17:32:44+00:00 | export-tests-green | 0 | 2.02 | `pytest -q tests/data_migration/test_export.py` | `c66f242844e31199` |  |  |
| 2026-11-16T17:33:04+00:00 | idiom-lint | 1 | 0.03 | `ruff check` | `c2072f4001a52dde` | Found 1 error. |  |
| 2026-11-16T17:33:11+00:00 | idiom-lint | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T17:33:11+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `1f97a1d50d41ccc4` |  |  |
| 2026-11-16T17:33:17+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-16T17:33:17+00:00 | idiom-lint | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T17:33:20+00:00 | export-tests-green | 0 | 2.02 | `pytest -q tests/data_migration/test_export.py` | `c66f242844e31199` |  |  |
| 2026-11-16T17:33:48+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:33:48+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T17:33:49+00:00 | data-load | 1 | 0.42 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot --mapping .migration/data/mapping.yaml` | `39d84694036a43bc` | Traceback (most recent call last): |  |
| 2026-11-16T17:33:59+00:00 | db-migrate | 0 | 0.49 | `python manage.py migrate --noinput` | `56d728c244009843` |  |  |
| 2026-11-16T17:33:59+00:00 | data-load | 0 | 0.44 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot --mapping .migration/data/mapping.yaml` | `102e06696c233e34` |  |  |
| 2026-11-16T17:34:00+00:00 | data-export | 0 | 0.43 | `python manage.py export_data_snapshot --mapping .migration/data/mapping.yaml --out .migration/data/target-export` | `ba754ea10ff616fb` |  |  |
| 2026-11-16T17:34:00+00:00 | data-reconcile | 0 | 0.08 | `python .migration/harness/tools/data_reconcile.py reconcile --snapshot .migration/data/snapshot --target .migration/data/target-export --mapping .migration/data/mapping.yaml --report /tmp/DM-05D-reconciliation.md` | `0e5f155ede36068f` |  | gate=data-reconcile tables=6 rows=54 mismatched_tables=0 |
