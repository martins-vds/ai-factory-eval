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
| 2026-11-16T15:38:48+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:38:49+00:00 | build-django-check | 0 | 0.28 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T15:38:49+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `6ddf6bd7eb02a775` | Found 1 error. |  |
| 2026-11-16T15:38:58+00:00 | idiom-ruff-check-rerun | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T15:38:58+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `45e10046d860b9ec` |  |  |
| 2026-11-16T15:39:06+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T15:39:06+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-16T15:39:49+00:00 | behavior-suite | 0 | 39.38 | `pytest -q` | `9b40dfddd90a1f48` |  |  |
| 2026-11-16T15:40:42+00:00 | crap-coverage-suite | 0 | 45.25 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `a7e7f9493f698801` |  |  |
| 2026-11-16T15:40:42+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T15:40:42+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-16T15:40:47+00:00 | mutation-changed | 0 | 0.07 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-16T15:41:27+00:00 | regression-focused | 0 | 1.81 | `pytest -q tests/data_migration/test_invariants.py` | `4c0f8168efad3556` |  |  |
