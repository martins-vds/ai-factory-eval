# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T00:43:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:44:14+00:00 | snapshot-validate | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-23T00:45:54+00:00 | invariants-tests | 0 | 3.79 | `pytest -q tests/data_migration/test_invariants.py` | `a74327c91ade8719` |  |  |
| 2026-11-23T00:46:11+00:00 | invariants-tests | 0 | 2.31 | `pytest -q tests/data_migration/test_invariants.py` | `04df3eebc456fd69` |  |  |
| 2026-11-23T00:46:27+00:00 | build-compileall | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:46:28+00:00 | build-django-check | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T00:47:27+00:00 | tests-full | 0 | 59.34 | `pytest -q` | `69f4617b0b7c4f11` |  |  |
| 2026-11-23T00:47:27+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:47:27+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T00:47:28+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-23T00:47:28+00:00 | idiom-ui | 0 | 0.69 | `python .migration/harness/tools/check_ui.py` | `e0b348f3d0ddff8c` |  | gate=ui scope="templates changed since 9820329e84d16f6c3d8a3b96ec790292948a0b83" templates=0 findings=0 |
| 2026-11-23T00:48:27+00:00 | crap-coverage | 0 | 58.06 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `b2727c485608a057` |  |  |
| 2026-11-23T00:48:27+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:48:27+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-23T00:48:27+00:00 | mutation-changed | 0 | 0.1 | `python .migration/harness/tools/afs-mutation` | `c99f8adbe9d09fb8` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=9820329e84d16f6c3d8a3b96ec790292948a0b83 |
