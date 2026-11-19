# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T21:39:59+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:43:40+00:00 | invariants-red | 2 | 3.02 | `pytest -q tests/data_migration/test_invariants.py` | `2b4dad968ade4654` | ___________ ERROR collecting tests/data_migration/test_invariants.py ___________ |  |
| 2026-11-19T21:43:51+00:00 | invariants | 1 | 2.22 | `pytest -q tests/data_migration/test_invariants.py` | `f51031e9a9874c56` | assert cargos |  |
| 2026-11-19T21:44:11+00:00 | invariants | 0 | 2.07 | `pytest -q tests/data_migration/test_invariants.py` | `f56eadf3d7746ccb` |  |  |
