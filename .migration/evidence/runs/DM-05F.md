# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T17:29:07+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:30:46+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-16T17:32:40+00:00 | fixture-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-16T17:33:08+00:00 | invariant-tests | 1 | 3.54 | `pytest -q tests/data_migration/test_invariants.py` | `ea06bcdf8e584a52` | E           TypeError: A handling activity requires a location |  |
| 2026-11-16T17:33:32+00:00 | invariant-tests | 1 | 1.72 | `pytest -q tests/data_migration/test_invariants.py` | `1baff2dcecfc2bc4` | assert cargos |  |
| 2026-11-16T17:33:40+00:00 | invariant-tests | 0 | 1.71 | `pytest -q tests/data_migration/test_invariants.py` | `14966a85db57e41f` |  |  |
| 2026-11-16T17:34:40+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T17:34:44+00:00 | build-check | 0 | 0.33 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T17:34:48+00:00 | idiom-ruff | 1 | 0.02 | `ruff check` | `eae8e1a80e689a7a` | Found 1 error. |  |
| 2026-11-16T17:34:56+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T17:35:00+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `22b85086c102e030` | 121 \|         assert derived_delivery.eta.date() == cargo.delivery.eta.date() |  |
| 2026-11-16T17:35:08+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-16T17:35:51+00:00 | behavior | 0 | 38.8 | `pytest -q` | `dd7fd720a395023c` |  |  |
| 2026-11-16T17:36:31+00:00 | crap-coverage | 0 | 36.22 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `849ecb43021fdb5c` |  |  |
| 2026-11-16T17:36:35+00:00 | crap-lizard | 0 | 0.11 | `lizard --csv src` | `9981c28b2c9fc005` |  |  |
| 2026-11-16T17:36:38+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `322822f1b6bcbeac` |  | gate=crap max=4.0 threshold=30 over=0 methods=15 |
| 2026-11-16T17:36:42+00:00 | mutation-changed | 0 | 0.06 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
