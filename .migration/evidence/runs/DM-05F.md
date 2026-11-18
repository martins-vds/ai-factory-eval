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
| 2026-11-18T04:00:01+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T04:00:01+00:00 | build-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T04:00:06+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T04:00:06+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T04:00:06+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T04:00:07+00:00 | idiom-ui | 0 | 0.49 | `python .migration/harness/tools/check_ui.py` | `2c84478523e8216f` |  | gate=ui scope="templates changed since d091ca0dc5db879d8f77656aa814694431c9a171" templates=0 findings=0 |
| 2026-11-18T04:01:00+00:00 | crap-coverage | 0 | 48.02 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `22eff43e0c573868` |  |  |
| 2026-11-18T04:01:01+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T04:01:01+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-18T04:01:07+00:00 | mutation-changed | 0 | 0.08 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-18T04:03:02+00:00 | regression | 0 | 46.92 | `pytest -q` | `4cdd2b1754cae2ad` |  |  |
| 2026-11-18T04:07:32+00:00 | invariants-review-fix | 0 | 2.07 | `pytest -q tests/data_migration/test_invariants.py` | `3c694261c1f3a68b` |  |  |
| 2026-11-18T04:07:32+00:00 | format-review-fix | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-18T04:09:01+00:00 | snapshot-final | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-18T04:09:01+00:00 | build-compile-final | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T04:09:01+00:00 | build-check-final | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T04:09:03+00:00 | behavior-final | 0 | 2.11 | `pytest -q tests/data_migration/test_invariants.py` | `8a5170c47238fc99` |  |  |
| 2026-11-18T04:09:08+00:00 | idiom-ruff-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T04:09:08+00:00 | idiom-format-final | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T04:09:09+00:00 | idiom-layers-final | 0 | 0.15 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T04:09:09+00:00 | idiom-ui-final | 0 | 0.5 | `python .migration/harness/tools/check_ui.py` | `2c84478523e8216f` |  | gate=ui scope="templates changed since d091ca0dc5db879d8f77656aa814694431c9a171" templates=0 findings=0 |
| 2026-11-18T04:10:01+00:00 | crap-coverage-final | 0 | 46.63 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `9205936e66c6506d` |  |  |
| 2026-11-18T04:10:02+00:00 | crap-lizard-final | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T04:10:02+00:00 | crap-score-final | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
