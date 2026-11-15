# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T05:46:20+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T05:47:07+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot/` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-15T05:51:15+00:00 | red-cargo-history | 1 | 4.78 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_cargo_delivery_matches_its_handling_history` | `1688bbe5a8d90559` | E           TypeError: A handling activity requires a location |  |
| 2026-11-15T05:51:34+00:00 | cargo-history | 1 | 1.8 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_cargo_delivery_matches_its_handling_history` | `2c42ec62a11bfd2a` | E           ValueError: Voyage is not allowed with event type RECEIVE |  |
| 2026-11-15T05:51:56+00:00 | cargo-history | 0 | 1.78 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_cargo_delivery_matches_its_handling_history` | `dc865d24518196dc` |  |  |
| 2026-11-15T05:52:39+00:00 | cargo-itinerary | 0 | 1.87 | `pytest -q tests/data_migration/test_invariants.py -k 'cargo_delivery or itinerary_legs'` | `ee8f212993cfd548` |  |  |
| 2026-11-15T05:53:22+00:00 | handling-references | 1 | 2.04 | `pytest -q tests/data_migration/test_invariants.py -k 'cargo_delivery or itinerary_legs or handling_events'` | `026ec2c202bc4561` | >           assert replace(derived, last_event_id=history.most_recent_event_id) == cargo.delivery |  |
| 2026-11-15T05:53:55+00:00 | handling-references | 0 | 1.98 | `pytest -q tests/data_migration/test_invariants.py -k 'cargo_delivery or itinerary_legs or handling_events'` | `d135fa9edad3e0d7` |  |  |
| 2026-11-15T05:54:25+00:00 | invariants | 0 | 2.08 | `pytest -q tests/data_migration/test_invariants.py` | `9d5fd7842fa81bb4` |  |  |
| 2026-11-15T05:55:30+00:00 | invariants | 0 | 2.1 | `pytest -q tests/data_migration/test_invariants.py` | `10e96b85b3bd96cf` |  |  |
