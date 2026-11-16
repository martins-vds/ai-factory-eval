# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T15:29:26+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:30:17+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-16T15:34:46+00:00 | delivery-invariant-red | 1 | 3.4 | `pytest -q tests/data_migration/test_invariants.py` | `4a4af4b18d7fc4f4` | E           TypeError: A handling activity requires a location |  |
| 2026-11-16T15:35:36+00:00 | delivery-invariant-green | 0 | 1.41 | `pytest -q tests/data_migration/test_invariants.py` | `38e13be45293b3a0` |  |  |
| 2026-11-16T15:36:30+00:00 | itinerary-invariant-red | 1 | 1.42 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_itinerary_legs_connect` | `eba8a73704f9d0a6` | >       assert any(len(cargo.itinerary.legs) > 1 for cargo in cargos) |  |
| 2026-11-16T15:37:15+00:00 | delivery-itinerary-invariants | 0 | 1.5 | `pytest -q tests/data_migration/test_invariants.py` | `87ceaed897e66904` |  |  |
| 2026-11-16T15:37:29+00:00 | handling-reference-invariant | 0 | 1.39 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_handling_events_reference_existing_voyages_and_locations` | `38e13be45293b3a0` |  |  |
| 2026-11-16T15:37:45+00:00 | schedule-invariant | 0 | 1.64 | `pytest -q tests/data_migration/test_invariants.py` | `2c4bee1fcf8e59a9` |  |  |
