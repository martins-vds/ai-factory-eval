# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T13:42:32+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T13:44:28+00:00 | export-red | 1 | 1.7 | `pytest -q tests/data_migration/test_export.py` | `ddf8bdfc3bb92e4c` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-15T13:45:20+00:00 | export-green | 1 | 1.43 | `pytest -q tests/data_migration/test_export.py` | `ce0b766a7a1d0804` | assert {path.name for path in output.glob('*.csv')} == { |  |
| 2026-11-15T13:45:31+00:00 | export-tests | 0 | 1.4 | `pytest -q tests/data_migration/test_export.py` | `253008a853eae844` |  |  |
| 2026-11-15T13:46:41+00:00 | build | 0 | 0.5 | `bash -lc 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-15T13:46:42+00:00 | behavior | 0 | 1.4 | `pytest -q tests/data_migration/test_export.py` | `253008a853eae844` |  |  |
| 2026-11-15T13:46:42+00:00 | idiom | 1 | 0.2 | `bash -lc 'ruff check && ruff format --check'` | `7bf885b4f2f32a66` |  |  |
| 2026-11-15T13:46:53+00:00 | idiom | 0 | 0.18 | `bash -lc 'ruff check && ruff format --check'` | `178f4aac2b404dcb` |  |  |
| 2026-11-15T13:47:30+00:00 | regression | 0 | 37.19 | `pytest -q` | `846b55d3d7687175` |  |  |
| 2026-11-15T13:48:06+00:00 | crap | 0 | 36.02 | `bash -lc 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `35d1fe98b04fd873` |  | gate=crap max=26.0 threshold=30 over=0 methods=181 |
