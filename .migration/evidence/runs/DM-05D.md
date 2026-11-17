# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-17T21:45:34+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:47:43+00:00 | export-red | 1 | 2.63 | `python -m pytest -q tests/data_migration/test_export.py` | `6b587924d2c066e0` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-17T21:48:22+00:00 | export-tests | 0 | 2.16 | `python -m pytest -q tests/data_migration/test_export.py` | `483bd3660ffb0fe6` |  |  |
| 2026-11-17T21:48:45+00:00 | idiom | 0 | 0.02 | `bash -c 'ruff check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py && ruff format --check src/cargotracker/data_migration/exporter.py src/cargotracker/data_migration/management/commands/export_data_snapshot.py tests/data_migration/test_export.py'` | `c6486b51f4832493` |  |  |
| 2026-11-17T21:48:50+00:00 | build | 0 | 0.54 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
