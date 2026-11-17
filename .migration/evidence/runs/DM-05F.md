# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-17T21:16:14+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:18:47+00:00 | behavior | 1 | 3.82 | `pytest -q tests/data_migration/test_invariants.py` | `c8d29df8376b82e5` | E                   django.core.exceptions.FieldError: Cannot resolve keyword 'carriermovementrecord' into field. Choice |  |
| 2026-11-17T21:19:02+00:00 | behavior | 0 | 1.35 | `pytest -q tests/data_migration/test_invariants.py` | `517fd2020a108ba9` |  |  |
| 2026-11-17T21:19:30+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:19:33+00:00 | build-check | 0 | 0.25 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-17T21:19:36+00:00 | idiom-lint | 1 | 0.02 | `ruff check` | `fb26c741d39b2d59` | 171 \|         assert len(legs) > 1 |  |
| 2026-11-17T21:19:44+00:00 | idiom-lint | 1 | 0.01 | `ruff check` | `3ef83ff74f3405f2` | Found 1 error. |  |
| 2026-11-17T21:19:50+00:00 | idiom-lint | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:19:53+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-17T21:20:26+00:00 | regression | 0 | 29.99 | `pytest -q` | `caf7f45839306c7d` |  |  |
