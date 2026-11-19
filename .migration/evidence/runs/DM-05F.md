# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T14:16:25+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:18:56+00:00 | snapshot-check | 0 | 0.08 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-19T14:20:11+00:00 | delivery-invariant | 0 | 4.25 | `pytest -q tests/data_migration/test_invariants.py` | `27a58a68125c2fbb` |  |  |
| 2026-11-19T14:20:54+00:00 | invariants | 0 | 2.16 | `pytest -q tests/data_migration/test_invariants.py` | `8a5170c47238fc99` |  |  |
| 2026-11-19T14:21:26+00:00 | build-compileall | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:21:31+00:00 | build-django-check | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T14:21:34+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `8fb3714f5dd7474f` | 175 \|         assert all( |  |
| 2026-11-19T14:22:00+00:00 | idiom-ruff-check-rerun | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T14:22:03+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-19T14:22:07+00:00 | idiom-layers | 0 | 0.15 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T14:22:11+00:00 | idiom-ui | 0 | 0.54 | `python .migration/harness/tools/check_ui.py` | `6aad5fd13879c105` |  | gate=ui scope="templates changed since 3dec56f20b4648f8666e1a2b402c8ec62e751153" templates=0 findings=0 |
| 2026-11-19T14:23:09+00:00 | tests | 0 | 51.01 | `pytest -q` | `7006b41d62caadfc` |  |  |
| 2026-11-19T14:24:06+00:00 | crap-coverage | 0 | 49.53 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `382f278faf324b7a` |  |  |
| 2026-11-19T14:24:10+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:24:14+00:00 | crap-score | 0 | 0.05 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-19T14:24:35+00:00 | mutation-changed | 0 | 0.09 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
