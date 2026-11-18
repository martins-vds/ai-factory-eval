# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T13:08:58+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:14:30+00:00 | invariants | 0 | 3.8 | `pytest -q tests/data_migration/test_invariants.py` | `687835eb0dbb78bf` |  |  |
| 2026-11-18T13:15:40+00:00 | build-compileall | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:15:42+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T13:15:46+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `8459a4dfd16d8e76` | 191 \|         assert all( |  |
| 2026-11-18T13:15:58+00:00 | idiom-ruff-check-fix | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T13:16:01+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `c58a9ea3befd937a` | 172 \|         assert cargo.delivery.misdirected == derived.misdirected |  |
| 2026-11-18T13:16:21+00:00 | idiom-ruff-format-fix | 1 | 0.01 | `ruff format --check` | `30f060c7f44f57bc` |  |  |
| 2026-11-18T13:16:27+00:00 | idiom-ruff-format-final | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T13:16:30+00:00 | idiom-layers | 0 | 0.15 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T13:16:34+00:00 | idiom-ui | 0 | 0.51 | `python .migration/harness/tools/check_ui.py` | `02b26224a2c553ec` |  | gate=ui scope="templates changed since fa30180469cd6e75006c8265246bbdeb038185e4" templates=0 findings=0 |
| 2026-11-18T13:16:41+00:00 | invariants-final | 0 | 2.12 | `pytest -q tests/data_migration/test_invariants.py` | `578cebb7a3c297c1` |  |  |
| 2026-11-18T13:17:43+00:00 | regression | 0 | 58.82 | `pytest -q` | `b1a211e17f512896` |  |  |
| 2026-11-18T13:18:39+00:00 | crap-coverage | 0 | 50.66 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `a543c86b92299345` |  |  |
| 2026-11-18T13:18:43+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:18:46+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-18T13:18:52+00:00 | mutation-changed | 0 | 0.08 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-18T13:19:25+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T15:43:13+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T15:45:36+00:00 | data-snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-18T15:45:42+00:00 | data-load | 1 | 1.31 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot --mapping .migration/data/mapping.yaml` | `39d84694036a43bc` | Traceback (most recent call last): |  |
| 2026-11-18T15:45:59+00:00 | data-schema-migrate | 0 | 0.57 | `python manage.py migrate --noinput` | `56d728c244009843` |  |  |
| 2026-11-18T15:46:02+00:00 | data-load | 0 | 0.51 | `python manage.py load_data_snapshot --snapshot .migration/data/snapshot --mapping .migration/data/mapping.yaml` | `102e06696c233e34` |  |  |
| 2026-11-18T15:46:07+00:00 | data-export | 1 | 0.4 | `python manage.py export_data_snapshot --mapping .migration/data/mapping.yaml --out .migration/data/target-export` | `31ae69b6b6c19fa7` |  |  |
| 2026-11-18T15:46:48+00:00 | build-compileall | 0 | 0.08 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T15:46:48+00:00 | build-check | 0 | 0.44 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T15:47:46+00:00 | behavior | 0 | 57.92 | `pytest -q` | `3dfda8ac4bf83dc2` |  |  |
| 2026-11-18T15:47:46+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T15:47:47+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T15:47:47+00:00 | idiom-layers | 0 | 0.15 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T15:47:47+00:00 | idiom-ui | 0 | 0.49 | `python .migration/harness/tools/check_ui.py` | `02b26224a2c553ec` |  | gate=ui scope="templates changed since fa30180469cd6e75006c8265246bbdeb038185e4" templates=0 findings=0 |
| 2026-11-18T15:48:38+00:00 | crap-coverage | 0 | 50.63 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `6b18649bf9be5c4f` |  |  |
| 2026-11-18T15:48:38+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T15:48:38+00:00 | crap-score | 0 | 0.05 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-18T16:00:26+00:00 | behavior-null-voyage-reproducer | 1 | 3.89 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_handling_events_reference_existing_voyages_and_locations` | `b92a846be57336c6` | assert event_references |  |
| 2026-11-18T16:00:45+00:00 | invariants-null-voyage-fixed | 1 | 5.02 | `pytest -q tests/data_migration/test_invariants.py` | `482c7be0bec152af` | E                   django.core.exceptions.FieldError: Cannot resolve keyword 'type' into field. Choices are: cargo, car |  |
| 2026-11-18T16:00:59+00:00 | invariants-null-voyage-fixed | 0 | 4.55 | `pytest -q tests/data_migration/test_invariants.py` | `6e5e34b5f4f11c36` |  |  |
| 2026-11-18T16:02:27+00:00 | invariants-null-voyage-fixed | 0 | 4.13 | `pytest -q tests/data_migration/test_invariants.py` | `f329478ba065a40c` |  |  |
