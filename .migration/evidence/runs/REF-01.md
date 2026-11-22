# Run journal: REF-01

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T04:24:57+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:26:29+00:00 | tdd-red-schema-api | 2 | 3.64 | `pytest -q tests/data_migration/test_export.py` | `39c8a7f65b64fee1` | _____________ ERROR collecting tests/data_migration/test_export.py _____________ |  |
| 2026-11-22T04:26:55+00:00 | focused-export-tests | 0 | 2.56 | `pytest -q tests/data_migration/test_export.py` | `a8ae3ff2db0d1bfc` |  |  |
