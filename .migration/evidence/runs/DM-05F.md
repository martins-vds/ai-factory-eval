# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T02:00:53+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T02:01:38+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-16T02:05:22+00:00 | invariant-delivery-red | 1 | 3.86 | `pytest -q tests/data_migration/test_invariants.py` | `d9ec07bc7434764a` | E           TypeError: A handling activity requires a location |  |
| 2026-11-16T02:06:32+00:00 | invariants-targeted | 0 | 1.82 | `pytest -q tests/data_migration/test_invariants.py` | `8ef3627370199135` |  |  |
| 2026-11-16T02:06:46+00:00 | idiom-format-targeted | 1 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `3ed4963d3ccd1bb9` |  |  |
| 2026-11-16T02:06:46+00:00 | idiom-lint-targeted | 1 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `409707c878d7bbe1` | Found 1 error. |  |
| 2026-11-16T02:07:00+00:00 | invariants-targeted-recheck | 0 | 1.79 | `pytest -q tests/data_migration/test_invariants.py` | `8ef3627370199135` |  |  |
| 2026-11-16T02:07:00+00:00 | idiom-lint | 0 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T02:07:00+00:00 | idiom-format | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
