# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-17T21:42:29+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:45:14+00:00 | invariants | 0 | 4.08 | `pytest -q tests/data_migration/test_invariants.py` | `8a5170c47238fc99` |  |  |
| 2026-11-17T21:45:40+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:45:44+00:00 | build-check | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-17T21:45:46+00:00 | idiom-lint | 1 | 0.02 | `ruff check` | `31955aadf9a34987` | 171 \|         assert all( |  |
| 2026-11-17T21:46:09+00:00 | invariants-after-lint-fix | 0 | 1.62 | `pytest -q tests/data_migration/test_invariants.py` | `7bbfa9adac667373` |  |  |
| 2026-11-17T21:46:12+00:00 | idiom-lint-final | 1 | 0.01 | `ruff check` | `1d3ce8f044cb4e78` | Found 1 error. |  |
| 2026-11-17T21:46:17+00:00 | idiom-autofix | 0 | 0.01 | `ruff check --fix tests/data_migration/test_invariants.py` | `aac3a0503d8b9505` | Found 1 error (1 fixed, 0 remaining). |  |
| 2026-11-17T21:46:20+00:00 | idiom-lint-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:46:22+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
