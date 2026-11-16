# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T20:35:38+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:38:42+00:00 | export-red | 1 | 1.39 | `python -m pytest -q tests/data_migration/test_export.py` | `d999d3049b3b3741` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-16T20:39:16+00:00 | export-green | 1 | 1.08 | `python -m pytest -q tests/data_migration/test_export.py` | `09894a73a987a570` | >       assert _read_csv(out / 'location.csv') == [ |  |
| 2026-11-16T20:39:28+00:00 | export-green | 0 | 1.05 | `python -m pytest -q tests/data_migration/test_export.py` | `27d1253d12cbb0a1` |  |  |
| 2026-11-16T20:40:14+00:00 | export-green | 0 | 1.07 | `python -m pytest -q tests/data_migration/test_export.py` | `81efd79c27213e56` |  |  |
