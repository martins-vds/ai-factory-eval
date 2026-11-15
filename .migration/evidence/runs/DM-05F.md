# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T06:09:05+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T06:13:05+00:00 | fixture-snapshot-check | 0 | 0.07 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-15T06:14:14+00:00 | delivery-invariant | 0 | 3.89 | `pytest -q tests/data_migration/test_invariants.py` | `483bd3660ffb0fe6` |  |  |
| 2026-11-15T06:15:15+00:00 | delivery-itinerary-invariants | 0 | 2.04 | `pytest -q tests/data_migration/test_invariants.py` | `c00baeaf11bd9e48` |  |  |
| 2026-11-15T06:15:42+00:00 | loaded-business-invariants | 0 | 2.16 | `pytest -q tests/data_migration/test_invariants.py` | `f56eadf3d7746ccb` |  |  |
| 2026-11-15T06:16:05+00:00 | idiom-ruff-check | 1 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `19d7f8203a522dba` | 168 \|         assert all( |  |
| 2026-11-15T06:16:16+00:00 | idiom-ruff-check-rerun | 0 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T06:16:19+00:00 | idiom-format-check | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-15T06:16:25+00:00 | loaded-business-invariants-rerun | 0 | 2.12 | `pytest -q tests/data_migration/test_invariants.py` | `d54dcac94e4b7fc8` |  |  |
| 2026-11-15T06:16:46+00:00 | loaded-business-invariants-final | 0 | 2.04 | `pytest -q tests/data_migration/test_invariants.py` | `af038f625faaaee2` |  |  |
