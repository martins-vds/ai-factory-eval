# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T23:45:20+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:46:09+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-21T23:47:30+00:00 | export-red | 1 | 2.25 | `pytest -q tests/data_migration/test_export.py` | `91ef70aa4a01af63` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-21T23:48:06+00:00 | export-green | 0 | 2.01 | `pytest -q tests/data_migration/test_export.py` | `8178d932945c4da3` |  |  |
| 2026-11-21T23:48:23+00:00 | data-migration-tests | 0 | 5.61 | `pytest -q tests/data_migration` | `7b536d067d217eb0` |  |  |
| 2026-11-21T23:48:34+00:00 | export-utc-check | 0 | 2.01 | `pytest -q tests/data_migration/test_export.py` | `8178d932945c4da3` |  |  |
| 2026-11-21T23:48:41+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:48:41+00:00 | build-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T23:48:41+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:48:41+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `44e78b49361054e6` |  |  |
| 2026-11-21T23:48:54+00:00 | export-postformat | 0 | 5.51 | `pytest -q tests/data_migration` | `1c46cbe5c20c138f` |  |  |
| 2026-11-21T23:48:54+00:00 | idiom-format-final | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
