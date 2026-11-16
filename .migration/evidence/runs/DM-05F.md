# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T20:36:35+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:39:25+00:00 | fixture-snapshot | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-16T20:40:44+00:00 | invariants | 1 | 3.37 | `pytest -q tests/data_migration/test_invariants.py` | `e4e74d7943cfdbba` | E           ValueError: Voyage is not allowed with event type RECEIVE |  |
| 2026-11-16T20:41:03+00:00 | invariants | 0 | 1.66 | `pytest -q tests/data_migration/test_invariants.py` | `01b439f99d953570` |  |  |
| 2026-11-16T20:41:49+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:41:53+00:00 | build-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T20:41:57+00:00 | idiom-ruff | 1 | 0.02 | `ruff check` | `783826721e9b72b7` | 187 \|         assert all( |  |
| 2026-11-16T20:42:14+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T20:42:17+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `035cf9fe4f3afe99` |  |  |
| 2026-11-16T20:42:28+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-16T20:42:32+00:00 | invariants | 0 | 1.61 | `pytest -q tests/data_migration/test_invariants.py` | `43885598a71d1469` |  |  |
