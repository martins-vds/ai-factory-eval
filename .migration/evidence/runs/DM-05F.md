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
