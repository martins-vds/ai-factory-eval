# Run journal: REF-02

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T04:24:56+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:25:46+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T04:25:47+00:00 | build-django-check | 0 | 0.98 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T04:25:57+00:00 | behavior-focused | 0 | 11.48 | `pytest -q tests/fees/test_endpoints.py tests/fees/test_fee_calculation.py` | `907b96b79c505949` |  |  |
