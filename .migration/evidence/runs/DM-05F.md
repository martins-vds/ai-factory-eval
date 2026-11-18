# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T03:06:52+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:09:32+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-18T03:11:17+00:00 | invariants-red | 1 | 4.2 | `pytest -q tests/data_migration/test_invariants.py` | `0a7d0bcd225ba1e9` | E       TypeError: TempPathFactory.__init__() missing 4 required positional arguments: 'given_basetemp', 'retention_coun |  |
| 2026-11-18T03:11:26+00:00 | invariants | 0 | 2.11 | `pytest -q tests/data_migration/test_invariants.py` | `578cebb7a3c297c1` |  |  |
| 2026-11-18T03:12:13+00:00 | idiom-ruff | 1 | 0.03 | `ruff check` | `bdb8ee94ebe8ba12` | 149 \|         assert all( |  |
| 2026-11-18T03:12:33+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T03:12:38+00:00 | invariants | 0 | 2.12 | `pytest -q tests/data_migration/test_invariants.py` | `10e96b85b3bd96cf` |  |  |
