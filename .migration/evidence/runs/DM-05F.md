# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-17T21:05:16+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:09:41+00:00 | behavior | 0 | 3.83 | `pytest -q tests/data_migration/test_invariants.py` | `d3db388f4ecc4e6b` |  |  |
| 2026-11-17T21:10:10+00:00 | idiom-lint | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:10:14+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
