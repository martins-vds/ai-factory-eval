# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T13:08:52+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:11:38+00:00 | baseline-loader-tests | 0 | 6.01 | `pytest -q tests/data_migration/test_load.py` | `a76a90b3787b0b8a` |  |  |
| 2026-11-21T13:11:55+00:00 | delivery-invariant-red | 1 | 1.34 | `pytest -q tests/data_migration/test_invariants.py` | `fb6fd795f8023ebd` | E           TypeError: A handling activity requires a location |  |
| 2026-11-21T13:12:27+00:00 | delivery-invariant-green | 1 | 1.39 | `pytest -q tests/data_migration/test_invariants.py` | `547af73e0c79e9f7` | E           ValueError: 'USLA' is not a valid UN/LOCODE |  |
| 2026-11-21T13:12:35+00:00 | delivery-invariant-green | 0 | 1.36 | `pytest -q tests/data_migration/test_invariants.py` | `d56bb067bee130ff` |  |  |
