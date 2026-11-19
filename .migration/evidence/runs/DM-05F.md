# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T18:17:30+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:18:02+00:00 | snapshot-validation | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-19T18:21:12+00:00 | invariants-delivery | 0 | 4.01 | `pytest -q tests/data_migration/test_invariants.py` | `1c6b0233fa8cd732` |  |  |
| 2026-11-19T18:21:39+00:00 | invariants-delivery | 0 | 1.67 | `pytest -q tests/data_migration/test_invariants.py` | `941ba30613647e4a` |  |  |
| 2026-11-19T18:22:07+00:00 | invariants | 0 | 1.92 | `pytest -q tests/data_migration/test_invariants.py` | `bb19e66110651773` |  |  |
| 2026-11-19T18:22:42+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:22:42+00:00 | build-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T18:22:46+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `79acecc9eb6f220a` | Found 1 error. |  |
| 2026-11-19T18:22:53+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:22:53+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `16f8135ecb528083` | -         assert any(len(legs) > 1 for legs in itineraries) |  |
| 2026-11-19T18:23:04+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:23:04+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-19T18:23:06+00:00 | invariants | 0 | 1.92 | `pytest -q tests/data_migration/test_invariants.py` | `846f06875c7c84ed` |  |  |
