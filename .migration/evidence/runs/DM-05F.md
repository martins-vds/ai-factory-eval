# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T13:47:29+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:48:37+00:00 | snapshot-check | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-19T13:51:43+00:00 | invariants-red | 1 | 3.03 | `pytest -q tests/data_migration/test_invariants.py` | `c231d72a23360021` | assert cargo.delivery.last_event_id == history.most_recent_event_id |  |
| 2026-11-19T13:51:52+00:00 | invariants-green | 0 | 1.35 | `pytest -q tests/data_migration/test_invariants.py` | `517fd2020a108ba9` |  |  |
| 2026-11-19T13:52:58+00:00 | invariants-final-targeted | 0 | 1.59 | `pytest -q tests/data_migration/test_invariants.py` | `16aece7227088486` |  |  |
| 2026-11-19T13:53:40+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:53:41+00:00 | build-django-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T13:53:45+00:00 | idiom-ruff | 1 | 0.03 | `ruff check` | `76a3ef08f402cc1e` | 208 \|         assert previous.arrival_time <= following.departure_time |  |
| 2026-11-19T13:53:55+00:00 | idiom-ruff-recheck | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T13:53:55+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `6c2c8ad69d1171ae` | 166 \|         assert ( |  |
| 2026-11-19T13:54:05+00:00 | idiom-ruff-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T13:54:05+00:00 | idiom-format-final | 1 | 0.01 | `ruff format --check` | `5e24686d13bb4c52` | -         assert replace(derived_delivery, last_event_id=history.most_recent_event_id) == cargo.delivery |  |
| 2026-11-19T13:54:13+00:00 | idiom-ruff-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T13:54:13+00:00 | idiom-format-final | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-19T13:54:13+00:00 | idiom-layers | 0 | 0.09 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T13:54:13+00:00 | idiom-ui | 0 | 0.31 | `python .migration/harness/tools/check_ui.py` | `d93f236accf4ea55` |  | gate=ui scope="templates changed since e0c85ffb6d679db505825b514053fc09f5db184d" templates=0 findings=0 |
| 2026-11-19T13:54:53+00:00 | tests-full | 0 | 36.33 | `pytest -q` | `b5dad418f129a441` |  |  |
| 2026-11-19T13:55:30+00:00 | crap-coverage | 0 | 30.6 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `bcf037115f55c563` |  |  |
| 2026-11-19T13:55:30+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:55:30+00:00 | crap-analyze | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-19T13:55:35+00:00 | mutation-changed | 0 | 0.06 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
