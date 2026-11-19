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
| 2026-11-19T18:20:49+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:20:53+00:00 | build-check | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T18:20:55+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:20:58+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `353db9b8c78f5091` | 180 \|         assert cargo.delivery.last_event_id == history.most_recent_event_id |  |
| 2026-11-19T18:21:09+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-19T18:21:12+00:00 | idiom-layers | 0 | 0.15 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T18:21:15+00:00 | idiom-ui | 0 | 0.54 | `python .migration/harness/tools/check_ui.py` | `e167a3ab83981c8b` |  | gate=ui scope="templates changed since 147042df4d04f58b6a76ddf2510293b05ce8d587" templates=0 findings=0 |
| 2026-11-19T18:22:12+00:00 | behavior | 0 | 50.83 | `pytest -q` | `1144dbe55f89f7c5` |  |  |
| 2026-11-19T18:23:03+00:00 | crap-coverage | 0 | 48.62 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `63e85e962381072c` |  |  |
| 2026-11-19T18:23:07+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:23:10+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-19T18:23:14+00:00 | mutation-changed | 0 | 0.09 | `python .migration/harness/tools/afs-mutation` | `b5f295a186c40835` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=147042df4d04f58b6a76ddf2510293b05ce8d587 |
| 2026-11-19T18:26:12+00:00 | regression | 0 | 49.77 | `pytest -q` | `557acfb279e59f8f` |  |  |
