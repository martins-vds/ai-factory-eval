# Run journal: REF-02

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T14:31:02+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T14:32:14+00:00 | targeted-idiom | 0 | 0.01 | `ruff check src/fees/views.py src/fees/presentation.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T14:32:25+00:00 | targeted-behavior | 0 | 11.25 | `pytest -q tests/fees/test_endpoints.py tests/fees/test_fee_calculation.py` | `baaf8873140f4e34` |  |  |
