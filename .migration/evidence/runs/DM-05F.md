# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T17:47:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T17:52:29+00:00 | invariants | 0 | 4.18 | `pytest -q tests/data_migration/test_invariants.py` | `99b46a9054cdd02b` |  |  |
| 2026-11-15T17:53:06+00:00 | idiom-focused | 1 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `a2d5ec536e477239` | 100 \|         assert all( |  |
| 2026-11-15T17:53:24+00:00 | idiom-focused | 0 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T17:53:24+00:00 | format-focused | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-15T17:53:27+00:00 | invariants | 0 | 2.21 | `pytest -q tests/data_migration/test_invariants.py` | `8a5170c47238fc99` |  |  |
