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
