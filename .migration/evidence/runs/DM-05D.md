# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T20:14:56+00:00 | export-red | 1 | 4.14 | `pytest -q tests/data_migration/test_export.py` | `e950bbb73cec134e` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-15T20:15:29+00:00 | export-focused | 0 | 1.97 | `pytest -q tests/data_migration/test_export.py` | `67ecf94f55b8e441` |  |  |
| 2026-11-15T20:15:59+00:00 | export-focused-final | 0 | 2.04 | `pytest -q tests/data_migration/test_export.py` | `8f6abe38f9b13362` |  |  |
| 2026-11-15T20:16:22+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T20:16:27+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T20:16:32+00:00 | idiom-ruff | 1 | 0.02 | `ruff check` | `dc19426542e87af7` | Found 1 error. |  |
| 2026-11-15T20:16:42+00:00 | idiom-ruff-rerun | 1 | 0.01 | `ruff check` | `302f11c4355c4b5f` | Found 1 error. |  |
