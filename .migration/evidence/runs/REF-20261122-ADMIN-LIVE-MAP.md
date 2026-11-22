# Run journal: REF-20261122-ADMIN-LIVE-MAP

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T22:46:07+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T22:47:01+00:00 | build | 0 | 0.62 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-22T22:47:05+00:00 | behavior | 0 | 3.56 | `pytest -q tests/cargo/interfaces/test_admin_live_map_data.py` | `63aef4cf81f042b1` |  |  |
| 2026-11-22T22:47:08+00:00 | spec | 0 | 0.07 | `python .migration/harness/tools/afs-spec run` | `1b0b939f3e1e502f` |  | gate=spec cases=0 failed=0 pending=0 |
| 2026-11-22T22:47:08+00:00 | idiom | 1 | 0.03 | `bash -c 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `4114b5fee6bdda0c` | Found 1 error. |  |
| 2026-11-22T22:47:14+00:00 | idiom | 1 | 0.01 | `bash -c 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `8bd8b7309d96680f` |  |  |
| 2026-11-22T22:47:33+00:00 | idiom | 0 | 0.92 | `bash -c 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `4a5dfe716e047465` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=ui scope="templates changed since 76afffa45a5001faad7b11f84f55e7c38ba2dca8" templates=0 findings=0 |
| 2026-11-22T22:47:45+00:00 | idiom | 1 | 0.01 | `bash -c 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `35e37249e3119d29` | Found 1 error. |  |
| 2026-11-22T22:49:14+00:00 | regression | 0 | 74.74 | `pytest -q` | `3936ea32712c35d2` |  |  |
| 2026-11-22T22:50:27+00:00 | crap | 0 | 72.62 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `e041a79a0590211f` |  | gate=crap max=26.0 threshold=30 over=0 methods=213 |
| 2026-11-22T22:51:49+00:00 | mutation_changed | 0 | 79.32 | `python .migration/harness/tools/afs-mutation` | `5ea56f2aea43636d` |  | gate=mutation score=1.000 threshold=0.8 killed=36 survived=0 files=2 base=76afffa45a5001faad7b11f84f55e7c38ba2dca8 |
