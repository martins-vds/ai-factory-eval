# Run journal: DM-05D

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T15:03:09+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T15:06:05+00:00 | export-red | 1 | 2.4 | `pytest -q tests/data_migration/test_export.py` | `6067e86239bf77c9` | E               KeyError: 'export_data_snapshot' |  |
| 2026-11-15T15:07:01+00:00 | export-focused | 0 | 1.85 | `pytest -q tests/data_migration/test_export.py` | `407df310e417114f` |  |  |
| 2026-11-15T15:08:09+00:00 | idiom | 1 | 0.04 | `bash -c 'ruff check && ruff format --check'` | `2c72e69e737f146d` | Found 1 error. |  |
| 2026-11-15T15:08:10+00:00 | build | 0 | 0.46 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-15T15:09:00+00:00 | behavior-regression | 0 | 51.05 | `pytest -q` | `bf83c668d32d2292` |  |  |
| 2026-11-15T15:09:11+00:00 | idiom-final | 1 | 0.12 | `bash -c 'ruff check && ruff format --check'` | `b9e8fbe75e723ac2` | 37 \|         assert list(rows[0]) == list(spec['columns']) |  |
| 2026-11-15T15:09:11+00:00 | crap-complexity | 0 | 0.23 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T15:10:08+00:00 | crap-coverage | 0 | 57.26 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `062abfc89527f179` |  |  |
| 2026-11-15T15:10:14+00:00 | idiom-final | 1 | 0.03 | `bash -c 'ruff check && ruff format --check'` | `2ecf5aeaca63e6e7` |  |  |
| 2026-11-15T15:10:14+00:00 | crap-score | 0 | 0.05 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `7c282c5408e34959` |  | gate=crap max=26.0 threshold=30 over=0 methods=184 |
| 2026-11-15T15:10:27+00:00 | idiom-final | 0 | 0.03 | `bash -c 'ruff check && ruff format --check'` | `178f4aac2b404dcb` |  |  |
| 2026-11-15T15:10:27+00:00 | build-final | 0 | 0.42 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-15T15:10:29+00:00 | export-focused-final | 0 | 1.89 | `pytest -q tests/data_migration/test_export.py` | `407df310e417114f` |  |  |
| 2026-11-15T15:22:41+00:00 | null-marker-red | 1 | 1.91 | `pytest -q tests/data_migration/test_export.py` | `2c2649632ca013fd` | E       Failed: DID NOT RAISE CommandError |  |
| 2026-11-15T15:22:52+00:00 | export-focused-final | 0 | 2.04 | `pytest -q tests/data_migration/test_export.py` | `e8bd98ab1634e9c9` |  |  |
