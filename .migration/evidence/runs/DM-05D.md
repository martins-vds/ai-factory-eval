# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-20T00:34:38+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:38:07+00:00 | export-test-red | 1 | 2.81 | `pytest -q tests/data_migration/test_export.py` | `4fa8ca0dd56fe97b` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-20T00:39:12+00:00 | export-test-green | 1 | 1.54 | `pytest -q tests/data_migration/test_export.py` | `ab5daeeac359a746` | assert {path.stem for path in output.glob('*.csv')} == { |  |
| 2026-11-20T00:39:45+00:00 | export-test-green | 0 | 1.54 | `pytest -q tests/data_migration/test_export.py` | `a41ffd9d3e4191f8` |  |  |
| 2026-11-20T00:40:05+00:00 | export-ruff | 0 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:40:10+00:00 | export-format | 1 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `f702f15fe10ccbf9` | 43 \|         assert data[0] == list(spec['columns']) |  |
| 2026-11-20T00:40:17+00:00 | export-format-fix | 0 | 0.01 | `ruff format src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `292ab567521d3084` |  |  |
| 2026-11-20T00:40:27+00:00 | export-test-green | 0 | 1.51 | `pytest -q tests/data_migration/test_export.py` | `76a0f2a0e9a6c1a5` |  |  |
| 2026-11-20T00:40:30+00:00 | export-format-check | 0 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `eee76f865de5a9f2` |  |  |
| 2026-11-20T00:41:21+00:00 | export-test-green | 0 | 1.52 | `pytest -q tests/data_migration/test_export.py` | `76a0f2a0e9a6c1a5` |  |  |
| 2026-11-20T00:41:44+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-20T00:41:52+00:00 | export-ruff | 0 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:41:57+00:00 | export-format-check | 0 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `eee76f865de5a9f2` |  |  |
