# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T23:43:34+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:45:54+00:00 | export-tests-red | 1 | 2.32 | `pytest -q tests/data_migration/test_export.py` | `dd0f0098aa02026b` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-21T23:46:17+00:00 | export-tests | 0 | 2.01 | `pytest -q tests/data_migration/test_export.py` | `23aad8c8d530c077` |  |  |
| 2026-11-21T23:46:41+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:47:06+00:00 | export-order-test | 0 | 2.16 | `pytest -q tests/data_migration/test_export.py` | `a055b940d481c35c` |  |  |
| 2026-11-21T23:47:09+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `4dc53b3708192cdb` |  |  |
| 2026-11-21T23:47:14+00:00 | format-fix | 0 | 0.01 | `ruff format src/cargotracker/data_migration/exporter.py` | `413a709001976657` |  |  |
| 2026-11-21T23:47:16+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `2c0a2eb94d0401d1` |  |  |
