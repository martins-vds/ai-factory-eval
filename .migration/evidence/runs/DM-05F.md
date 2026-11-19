# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T18:17:30+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:18:02+00:00 | snapshot-validation | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-19T18:21:12+00:00 | invariants-delivery | 0 | 4.01 | `pytest -q tests/data_migration/test_invariants.py` | `1c6b0233fa8cd732` |  |  |
| 2026-11-19T18:21:39+00:00 | invariants-delivery | 0 | 1.67 | `pytest -q tests/data_migration/test_invariants.py` | `941ba30613647e4a` |  |  |
