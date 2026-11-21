# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T23:43:31+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:47:03+00:00 | invariants | 0 | 2.5 | `pytest -q tests/data_migration/test_invariants.py` | `eee6ca43739a8141` |  |  |
| 2026-11-21T23:47:44+00:00 | behavior | 0 | 2.09 | `pytest -q tests/data_migration/test_invariants.py` | `578cebb7a3c297c1` |  |  |
| 2026-11-21T23:48:14+00:00 | build | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:48:14+00:00 | build | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T23:48:17+00:00 | idiom | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:48:17+00:00 | idiom | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-21T23:48:18+00:00 | idiom | 0 | 0.15 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T23:48:18+00:00 | idiom | 0 | 0.65 | `python .migration/harness/tools/check_ui.py` | `2c9207ddc870d52a` |  | gate=ui scope="templates changed since 1b37381736b2a7e7df0d332af717fca83ebb6f81" templates=0 findings=0 |
| 2026-11-21T23:49:13+00:00 | crap | 0 | 49.52 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `b6820c9b56622a4b` |  |  |
| 2026-11-21T23:49:14+00:00 | crap | 0 | 0.15 | `sh -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:49:14+00:00 | crap | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-21T23:49:22+00:00 | mutation_changed | 0 | 0.09 | `python .migration/harness/tools/afs-mutation` | `50f0561554397f9b` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=1b37381736b2a7e7df0d332af717fca83ebb6f81 |
| 2026-11-21T23:50:13+00:00 | regression | 0 | 48.46 | `pytest -q` | `b346434dad1b9d74` |  |  |
