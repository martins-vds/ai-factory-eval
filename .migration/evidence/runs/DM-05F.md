# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T01:35:03+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:38:31+00:00 | invariants | 0 | 2.9 | `pytest -q tests/data_migration/test_invariants.py` | `7ed2738ac3dcd8f9` |  |  |
| 2026-11-23T01:38:48+00:00 | idiom-ruff | 1 | 0.02 | `ruff check` | `938d9cea43029b50` | 165 \|         assert all( |  |
| 2026-11-23T01:38:55+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T01:38:58+00:00 | invariants | 0 | 1.26 | `pytest -q tests/data_migration/test_invariants.py` | `db3aca357b581d38` |  |  |
| 2026-11-23T01:39:02+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `fe1a57e6ce5df523` | 138 \|     assert cargo is not None |  |
| 2026-11-23T01:39:08+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T01:39:11+00:00 | invariants | 0 | 1.19 | `pytest -q tests/data_migration/test_invariants.py` | `db3aca357b581d38` |  |  |
