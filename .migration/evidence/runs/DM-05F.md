# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-17T21:16:14+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:18:47+00:00 | behavior | 1 | 3.82 | `pytest -q tests/data_migration/test_invariants.py` | `c8d29df8376b82e5` | E                   django.core.exceptions.FieldError: Cannot resolve keyword 'carriermovementrecord' into field. Choice |  |
| 2026-11-17T21:19:02+00:00 | behavior | 0 | 1.35 | `pytest -q tests/data_migration/test_invariants.py` | `517fd2020a108ba9` |  |  |
