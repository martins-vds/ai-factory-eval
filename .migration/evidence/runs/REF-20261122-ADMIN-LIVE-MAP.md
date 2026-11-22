# Run journal: REF-20261122-ADMIN-LIVE-MAP

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T22:46:41+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T22:47:27+00:00 | behavior-before-refactor | 0 | 4.77 | `pytest -q tests/cargo/interfaces/test_admin_live_map_data.py` | `4586ecf3fb9d1b57` |  |  |
| 2026-11-22T22:48:18+00:00 | behavior-after-extraction-targeted | 0 | 3.12 | `pytest -q tests/cargo/interfaces/test_admin_live_map_data.py` | `3b03224376981219` |  |  |
| 2026-11-22T22:48:43+00:00 | build | 0 | 0.43 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-22T22:49:58+00:00 | behavior | 0 | 73.21 | `pytest -q` | `2eba49157cc4d50d` |  |  |
| 2026-11-22T22:50:01+00:00 | spec | 0 | 0.06 | `python .migration/harness/tools/afs-spec run` | `1b0b939f3e1e502f` |  | gate=spec cases=0 failed=0 pending=0 |
| 2026-11-22T22:50:03+00:00 | idiom | 1 | 0.03 | `bash -c 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `4b0cffdaef4f87fb` | Found 1 error. |  |
| 2026-11-22T22:50:11+00:00 | idiom | 0 | 0.76 | `bash -c 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `ef19c8bc89e3d1be` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=ui scope="templates changed since b6040f86168f81fb0e686dba820244aeb87ce1cb" templates=0 findings=0 |
| 2026-11-22T22:51:23+00:00 | crap | 0 | 69.35 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `770ba33d319fe460` |  | gate=crap max=26.0 threshold=30 over=0 methods=213 |
| 2026-11-22T22:52:45+00:00 | mutation_changed | 0 | 80.0 | `python .migration/harness/tools/afs-mutation` | `27a05fb4291dcda8` |  | gate=mutation score=1.000 threshold=0.8 killed=36 survived=0 files=2 base=b6040f86168f81fb0e686dba820244aeb87ce1cb |
| 2026-11-22T22:54:06+00:00 | regression | 0 | 79.2 | `pytest -q` | `ad70934050fd869f` |  |  |
