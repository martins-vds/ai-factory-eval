# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T23:45:51+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:46:01+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-21T23:48:35+00:00 | invariants | 0 | 3.74 | `pytest -q tests/data_migration/test_invariants.py` | `10e96b85b3bd96cf` |  |  |
| 2026-11-21T23:49:38+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:49:38+00:00 | build-django-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T23:49:38+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T23:49:39+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `7c5f42c9f0801405` | 84 \|             assert previous.arrival_time <= following.departure_time, voyage.voyage_number |  |
| 2026-11-21T23:49:47+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-21T23:49:47+00:00 | idiom-layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T23:49:48+00:00 | idiom-ui | 0 | 0.5 | `python .migration/harness/tools/check_ui.py` | `23c16a84dc6937da` |  | gate=ui scope="templates changed since 3342ac09c288306f1460ce4451f549197327b9cb" templates=0 findings=0 |
| 2026-11-21T23:49:49+00:00 | invariants-final | 0 | 1.84 | `pytest -q tests/data_migration/test_invariants.py` | `846f06875c7c84ed` |  |  |
| 2026-11-21T23:50:32+00:00 | regression | 0 | 38.81 | `pytest -q` | `c28544dfd838969e` |  |  |
| 2026-11-21T23:51:16+00:00 | crap-coverage | 0 | 38.91 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `daff9a25bcd1346a` |  |  |
| 2026-11-21T23:51:17+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:51:17+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-21T23:51:20+00:00 | mutation-changed | 0 | 0.08 | `python .migration/harness/tools/afs-mutation` | `ff38ed57dad3cb71` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=3342ac09c288306f1460ce4451f549197327b9cb |
| 2026-11-21T23:56:03+00:00 | final-invariants | 0 | 1.9 | `pytest -q tests/data_migration/test_invariants.py` | `fed06df9dc542900` |  |  |
| 2026-11-21T23:57:07+00:00 | build-compile-final | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T23:57:08+00:00 | build-check-final | 0 | 0.32 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T23:57:57+00:00 | finish-check | 0 | 41.99 | `python .migration/harness/tools/afs-finish-check --ticket DM-05F --role afs-migrator` | `a1b60371041f6195` |  | gate=finish-check ticket=DM-05F role=afs-migrator findings=0 |
