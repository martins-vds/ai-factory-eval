# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T18:13:54+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:17:47+00:00 | targeted-red | 1 | 4.6 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_cargo_delivery_state_matches_handling_history` | `e4e3f90706d056e3` | E           TypeError: A handling activity requires a location |  |
| 2026-11-19T18:18:32+00:00 | delivery-invariant | 1 | 1.9 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_cargo_delivery_state_matches_handling_history` | `18fd1b0cf616bad1` | assert cargo.delivery.last_event_id == history.most_recent_event_id |  |
| 2026-11-19T18:18:45+00:00 | delivery-invariant | 1 | 1.9 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_cargo_delivery_state_matches_handling_history` | `ef94edf5cc3f5724` | assert cargo.delivery.last_event_id == history.most_recent_event_id |  |
| 2026-11-19T18:18:55+00:00 | delivery-invariant | 0 | 1.86 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_cargo_delivery_state_matches_handling_history` | `81f0a73f6ef41a79` |  |  |
| 2026-11-19T18:19:10+00:00 | itinerary-invariant | 0 | 1.82 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_itinerary_legs_connect` | `67c681089d32fd8f` |  |  |
| 2026-11-19T18:19:21+00:00 | handling-reference-invariant | 0 | 1.83 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_handling_events_reference_existing_voyages_and_locations` | `263c94f24c6bf4b6` |  |  |
| 2026-11-19T18:19:30+00:00 | voyage-schedule-invariant | 0 | 1.84 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_voyage_carrier_movement_schedules_are_in_order` | `67c681089d32fd8f` |  |  |
| 2026-11-19T18:19:50+00:00 | invariants-targeted | 0 | 2.14 | `pytest -q tests/data_migration/test_invariants.py` | `1b10789e86b1daf8` |  |  |
