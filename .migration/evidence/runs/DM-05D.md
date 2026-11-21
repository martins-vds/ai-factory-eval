# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T13:08:47+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:09:17+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-21T13:11:30+00:00 | export-red | 1 | 2.97 | `pytest -q tests/data_migration/test_export.py` | `fa5a0d9acb31be9e` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-21T13:12:08+00:00 | export-green | 0 | 1.43 | `pytest -q tests/data_migration/test_export.py` | `38e13be45293b3a0` |  |  |
| 2026-11-21T13:12:24+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:12:27+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `460bba73f2dafa9b` |  |  |
| 2026-11-21T13:12:34+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
| 2026-11-21T13:12:39+00:00 | export-green | 0 | 1.43 | `pytest -q tests/data_migration/test_export.py` | `a558b8376cd28466` |  |  |
| 2026-11-21T13:13:27+00:00 | export-green | 1 | 1.49 | `pytest -q tests/data_migration/test_export.py` | `23c663417b9de9fb` | assert {path.stem for path in output.glob('*.csv')} == { |  |
| 2026-11-21T13:13:36+00:00 | export-green | 0 | 1.45 | `pytest -q tests/data_migration/test_export.py` | `f51873a8b2568bb4` |  |  |
