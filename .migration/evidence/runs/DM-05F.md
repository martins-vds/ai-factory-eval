# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T03:53:24+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:56:12+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-18T03:58:14+00:00 | invariants | 1 | 4.58 | `pytest -q tests/data_migration/test_invariants.py` | `40b0ae880e09b6c3` | ___ ERROR at setup of test_cargo_delivery_state_matches_its_handling_history ___ |  |
| 2026-11-18T03:58:25+00:00 | invariants | 1 | 2.1 | `pytest -q tests/data_migration/test_invariants.py` | `2c4c300f59412b25` | E           ValueError: Voyage is not allowed with event type RECEIVE |  |
| 2026-11-18T03:58:41+00:00 | invariants | 1 | 2.11 | `pytest -q tests/data_migration/test_invariants.py` | `967fd8d855e48228` | >           assert replace(derived_delivery, last_event_id=history.most_recent_event_id) == ( |  |
| 2026-11-18T03:59:03+00:00 | invariants | 0 | 2.06 | `pytest -q tests/data_migration/test_invariants.py` | `3c694261c1f3a68b` |  |  |
| 2026-11-18T03:59:17+00:00 | format-check | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
