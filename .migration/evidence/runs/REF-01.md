# Run journal: REF-01

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T04:20:14+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:21:14+00:00 | schema-contract-red | 2 | 1.71 | `pytest -q tests/data_migration/test_export.py -k 'model_index_excludes or interprets_naive'` | `4c598d19a762a646` | _____________ ERROR collecting tests/data_migration/test_export.py _____________ |  |
| 2026-11-22T04:21:33+00:00 | export-tests | 0 | 1.52 | `pytest -q tests/data_migration/test_export.py` | `a5b90414d6a07cbc` |  |  |
