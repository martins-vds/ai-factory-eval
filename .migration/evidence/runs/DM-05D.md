# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T00:43:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:45:29+00:00 | export-red | 1 | 3.06 | `pytest -q tests/data_migration/test_export.py` | `3adc374330483331` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-23T00:46:02+00:00 | export-roundtrip | 0 | 1.85 | `pytest -q tests/data_migration/test_export.py` | `263c94f24c6bf4b6` |  |  |
| 2026-11-23T00:46:09+00:00 | focused-ruff | 1 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `9687f4fe36876830` | Found 1 error. |  |
| 2026-11-23T00:46:13+00:00 | focused-ruff-fix | 0 | 0.01 | `ruff check --fix src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `aac3a0503d8b9505` | Found 1 error (1 fixed, 0 remaining). |  |
| 2026-11-23T00:46:29+00:00 | focused-ruff | 1 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `25c7cc9cdc176530` | Found 1 error. |  |
| 2026-11-23T00:46:31+00:00 | export-focused-tests | 0 | 1.98 | `pytest -q tests/data_migration/test_export.py` | `88926c1833d969b0` |  |  |
| 2026-11-23T00:46:34+00:00 | focused-ruff-fix | 0 | 0.01 | `ruff check --fix src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `aac3a0503d8b9505` | Found 1 error (1 fixed, 0 remaining). |  |
| 2026-11-23T00:46:40+00:00 | focused-ruff | 0 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:46:40+00:00 | focused-format | 1 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `17df3cf70f917d74` |  |  |
| 2026-11-23T00:46:42+00:00 | export-focused-tests-final | 0 | 2.08 | `pytest -q tests/data_migration/test_export.py` | `8f6abe38f9b13362` |  |  |
| 2026-11-23T00:46:45+00:00 | focused-format-fix | 0 | 0.01 | `ruff format src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `44b7183e1f210a48` |  |  |
| 2026-11-23T00:46:56+00:00 | focused-ruff-final | 0 | 0.01 | `ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:46:57+00:00 | focused-format-final | 0 | 0.01 | `ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `eee76f865de5a9f2` |  |  |
| 2026-11-23T00:46:58+00:00 | export-focused-tests-final | 0 | 2.07 | `pytest -q tests/data_migration/test_export.py` | `7dae9c85117603cd` |  |  |
