# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T03:58:09+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T04:00:55+00:00 | export-red | 1 | 2.25 | `python -m pytest -q tests/data_migration/test_export.py` | `993e34b993731366` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-16T04:01:29+00:00 | export-tests | 0 | 1.85 | `python -m pytest -q tests/data_migration/test_export.py` | `263c94f24c6bf4b6` |  |  |
| 2026-11-16T04:01:41+00:00 | idiom-lint-targeted | 1 | 0.01 | `ruff check src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `43b474df297a441d` | 62 \|     assert carrier_movement['departure_time'] == '2026-11-08T12:00:00Z' |  |
| 2026-11-16T04:01:41+00:00 | idiom-format-targeted | 1 | 0.01 | `ruff format --check src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `4b0b9321e6532ba2` | 44 \|     except OSError as error: |  |
| 2026-11-16T04:01:52+00:00 | format-targeted | 0 | 0.01 | `ruff format src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `10869b88a75066aa` |  |  |
| 2026-11-16T04:01:56+00:00 | idiom-format-targeted-rerun | 0 | 0.01 | `ruff format --check src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `3bc53bf3e981a98a` |  |  |
| 2026-11-16T04:01:56+00:00 | idiom-lint-targeted-rerun | 0 | 0.01 | `ruff check src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T04:01:58+00:00 | export-tests-rerun | 0 | 1.87 | `python -m pytest -q tests/data_migration/test_export.py` | `67c681089d32fd8f` |  |  |
