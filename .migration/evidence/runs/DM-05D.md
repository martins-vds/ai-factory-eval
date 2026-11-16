# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T02:00:16+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:03:25+00:00 | export-red | 1 | 1.85 | `python -m pytest -q tests/data_migration/test_export.py` | `bf8f7730b08cb74a` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-16T02:04:16+00:00 | export-green | 0 | 1.57 | `python -m pytest -q tests/data_migration/test_export.py` | `313e5831c83bcc34` |  |  |
| 2026-11-16T02:04:53+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:04:53+00:00 | build-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T02:04:53+00:00 | idiom-lint | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T02:04:53+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `81f34237d741babf` |  |  |
| 2026-11-16T02:05:07+00:00 | idiom-format-rerun | 0 | 0.01 | `ruff format --check` | `c7a0bcb17dd5241a` |  |  |
| 2026-11-16T02:05:09+00:00 | export-regression | 0 | 1.52 | `python -m pytest -q tests/data_migration/test_export.py` | `7bc5776d19eed069` |  |  |
