# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T16:23:01+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T16:26:25+00:00 | build | 0 | 0.69 | `sh -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-19T16:26:26+00:00 | idiom | 0 | 0.78 | `sh -c 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `8f84d1f3ceb64262` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=ui scope="templates changed since d3d368d02643993ce038911088a3f2373a53d8ca" templates=0 findings=0 |
| 2026-11-19T16:26:31+00:00 | behavior | 0 | 6.27 | `pytest -q tests/data_migration` | `546f480a6548cc2b` |  |  |
| 2026-11-19T16:26:34+00:00 | mutation_changed | 0 | 0.1 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-19T16:27:29+00:00 | regression | 0 | 52.3 | `pytest -q` | `9bf858a1d6a20918` |  |  |
| 2026-11-19T16:28:25+00:00 | crap | 0 | 49.19 | `sh -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `02185ca7a0984a5f` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-19T16:29:34+00:00 | behavior-final | 0 | 2.66 | `pytest -q tests/data_migration/test_invariants.py` | `44cc03476d246aff` |  |  |
