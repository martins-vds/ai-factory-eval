# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T13:08:52+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:11:38+00:00 | baseline-loader-tests | 0 | 6.01 | `pytest -q tests/data_migration/test_load.py` | `a76a90b3787b0b8a` |  |  |
| 2026-11-21T13:11:55+00:00 | delivery-invariant-red | 1 | 1.34 | `pytest -q tests/data_migration/test_invariants.py` | `fb6fd795f8023ebd` | E           TypeError: A handling activity requires a location |  |
| 2026-11-21T13:12:27+00:00 | delivery-invariant-green | 1 | 1.39 | `pytest -q tests/data_migration/test_invariants.py` | `547af73e0c79e9f7` | E           ValueError: 'USLA' is not a valid UN/LOCODE |  |
| 2026-11-21T13:12:35+00:00 | delivery-invariant-green | 0 | 1.36 | `pytest -q tests/data_migration/test_invariants.py` | `d56bb067bee130ff` |  |  |
| 2026-11-21T13:12:57+00:00 | itinerary-invariant | 0 | 1.47 | `pytest -q tests/data_migration/test_invariants.py` | `fdbdbde72766e543` |  |  |
| 2026-11-21T13:13:06+00:00 | handling-reference-invariant | 0 | 1.46 | `pytest -q tests/data_migration/test_invariants.py` | `01380a3c1311fd50` |  |  |
| 2026-11-21T13:13:14+00:00 | movement-schedule-invariant | 0 | 1.56 | `pytest -q tests/data_migration/test_invariants.py` | `2ab521d85429af10` |  |  |
| 2026-11-21T13:13:20+00:00 | idiom-targeted | 1 | 0.01 | `bash -c 'ruff check tests/data_migration/test_invariants.py && ruff format --check tests/data_migration/test_invariants.py'` | `db7757f211641d76` | 152 \|         assert all( |  |
| 2026-11-21T13:13:33+00:00 | idiom-targeted | 0 | 0.02 | `bash -c 'ruff check tests/data_migration/test_invariants.py && ruff format --check tests/data_migration/test_invariants.py'` | `ce04ce92b1607300` |  |  |
| 2026-11-21T13:13:35+00:00 | invariants-targeted | 0 | 1.55 | `pytest -q tests/data_migration/test_invariants.py` | `2ab521d85429af10` |  |  |
| 2026-11-21T13:14:37+00:00 | idiom-targeted | 0 | 0.01 | `bash -c 'ruff check tests/data_migration/test_invariants.py && ruff format --check tests/data_migration/test_invariants.py'` | `ce04ce92b1607300` |  |  |
| 2026-11-21T13:14:38+00:00 | invariants-targeted | 1 | 1.58 | `pytest -q tests/data_migration/test_invariants.py` | `9eff7d0d45037b32` | >           assert ( |  |
| 2026-11-21T13:14:45+00:00 | idiom-targeted | 0 | 0.02 | `bash -c 'ruff check tests/data_migration/test_invariants.py && ruff format --check tests/data_migration/test_invariants.py'` | `ce04ce92b1607300` |  |  |
| 2026-11-21T13:14:47+00:00 | invariants-targeted | 0 | 1.57 | `pytest -q tests/data_migration/test_invariants.py` | `ff8b70c9209cc2a9` |  |  |
| 2026-11-21T13:15:08+00:00 | build | 0 | 0.33 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-21T13:15:08+00:00 | idiom | 0 | 0.56 | `bash -c 'ruff check && ruff format --check && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `d7492e875162a0bc` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=ui scope="templates changed since e57046602af0a3d7f05e7dc272992c38cf7c1d64" templates=0 findings=0 |
| 2026-11-21T13:15:52+00:00 | crap | 0 | 39.25 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `b1d558cd7139cd02` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-21T13:15:54+00:00 | mutation_changed | 0 | 0.07 | `python .migration/harness/tools/afs-mutation` | `70f03876a5c9fd59` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=e57046602af0a3d7f05e7dc272992c38cf7c1d64 |
| 2026-11-21T13:16:38+00:00 | behavior | 0 | 37.72 | `pytest -q` | `df49d9bd7055ec7a` |  |  |
| 2026-11-21T13:17:47+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-21T13:18:57+00:00 | regression | 0 | 38.26 | `pytest -q` | `600255365b16431f` |  |  |
