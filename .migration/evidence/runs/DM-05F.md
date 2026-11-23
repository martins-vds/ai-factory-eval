# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T00:43:54+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:44:48+00:00 | snapshot-check | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-23T00:47:20+00:00 | invariants | 0 | 4.01 | `pytest -q tests/data_migration/test_invariants.py` | `593ffc4878763a58` |  |  |
| 2026-11-23T00:47:33+00:00 | ruff-check | 1 | 0.02 | `ruff check` | `f70d8d5aa1b2fd12` | 214 \|             assert movement.departure_time < movement.arrival_time |  |
| 2026-11-23T00:47:33+00:00 | ruff-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T00:47:34+00:00 | invariants | 0 | 1.29 | `pytest -q tests/data_migration/test_invariants.py` | `a4f90380a50f47a8` |  |  |
| 2026-11-23T00:47:41+00:00 | ruff-check | 1 | 0.01 | `ruff check` | `d9a983064f4b09fd` | Found 1 error. |  |
| 2026-11-23T00:47:41+00:00 | ruff-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T00:47:43+00:00 | invariants | 0 | 1.21 | `pytest -q tests/data_migration/test_invariants.py` | `e1e76aa649e63250` |  |  |
| 2026-11-23T00:47:49+00:00 | ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:47:49+00:00 | ruff-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T00:47:50+00:00 | invariants | 0 | 1.21 | `pytest -q tests/data_migration/test_invariants.py` | `ace756f276043610` |  |  |
| 2026-11-23T00:48:49+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T00:48:50+00:00 | build-check | 0 | 0.23 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T00:48:52+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T00:48:52+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T00:48:52+00:00 | idiom-layers | 0 | 0.09 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-23T00:48:53+00:00 | idiom-ui | 0 | 0.37 | `python .migration/harness/tools/check_ui.py` | `f800a5a3a569046c` |  | gate=ui scope="templates changed since 2d36ef5d87b68c6a28719854e3a11d8e2ba337e9" templates=0 findings=0 |
| 2026-11-23T00:49:25+00:00 | regression | 0 | 28.85 | `pytest -q` | `ab3d68438b3660da` |  |  |
| 2026-11-23T00:49:56+00:00 | crap-coverage | 0 | 26.86 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `0852712a14ba4820` |  |  |
| 2026-11-23T00:49:56+00:00 | crap-lizard | 0 | 0.08 | `lizard --csv src` | `9981c28b2c9fc005` |  |  |
| 2026-11-23T00:49:56+00:00 | crap-score | 0 | 0.02 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `322822f1b6bcbeac` |  | gate=crap max=4.0 threshold=30 over=0 methods=15 |
| 2026-11-23T00:49:59+00:00 | mutation-changed | 0 | 0.05 | `python .migration/harness/tools/afs-mutation` | `e5ad16d01fdd27c1` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=2d36ef5d87b68c6a28719854e3a11d8e2ba337e9 |
| 2026-11-23T00:51:11+00:00 | validate | 0 | 4.0 | `python .migration/harness/tools/validate.py .migration` | `b05e2a864e5153ee` |  |  |
| 2026-11-23T00:51:42+00:00 | final-validate | 0 | 4.1 | `python .migration/harness/tools/validate.py .migration` | `b05e2a864e5153ee` |  |  |
