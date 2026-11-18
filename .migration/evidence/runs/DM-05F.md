# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T03:47:33+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:50:57+00:00 | invariants-targeted | 1 | 3.64 | `python -m pytest -q tests/data_migration/test_invariants.py` | `3785c977312d9bfa` | assert cargos |  |
| 2026-11-18T03:51:11+00:00 | invariants-targeted | 0 | 1.79 | `python -m pytest -q tests/data_migration/test_invariants.py` | `c89facfcfcbcdc9f` |  |  |
| 2026-11-18T03:51:33+00:00 | idiom-focused | 1 | 0.02 | `bash -c 'ruff check tests/data_migration/test_invariants.py && ruff format --check tests/data_migration/test_invariants.py'` | `9f624f518144a56a` |  |  |
| 2026-11-18T03:51:38+00:00 | idiom-focused | 0 | 0.01 | `bash -c 'ruff check tests/data_migration/test_invariants.py && ruff format --check tests/data_migration/test_invariants.py'` | `ce04ce92b1607300` |  |  |
| 2026-11-18T03:51:53+00:00 | invariants-targeted | 0 | 1.82 | `python -m pytest -q tests/data_migration/test_invariants.py` | `c22487a850faaa14` |  |  |
| 2026-11-18T03:52:28+00:00 | build | 0 | 0.39 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-18T03:52:33+00:00 | behavior | 0 | 1.82 | `python -m pytest -q tests/data_migration/test_invariants.py` | `593ffc4878763a58` |  |  |
| 2026-11-18T03:52:36+00:00 | idiom | 0 | 0.56 | `bash -c 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `ccb05c5f5f09a98f` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=ui scope="templates changed since 57bcbcbeb308f3f06719a8a7a871fcf04602f905" templates=0 findings=0 |
| 2026-11-18T03:53:27+00:00 | crap | 0 | 45.43 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `edf206fa81ca2a41` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-18T03:54:15+00:00 | regression | 0 | 43.38 | `pytest -q` | `0663a2a86debb7bb` |  |  |
| 2026-11-18T03:54:25+00:00 | mutation-changed | 0 | 0.07 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-18T03:59:53+00:00 | idiom-focused | 0 | 0.02 | `bash -c 'ruff check tests/data_migration/test_invariants.py && ruff format --check tests/data_migration/test_invariants.py'` | `ce04ce92b1607300` |  |  |
| 2026-11-18T03:59:55+00:00 | behavior | 0 | 1.93 | `python -m pytest -q tests/data_migration/test_invariants.py` | `fed06df9dc542900` |  |  |
