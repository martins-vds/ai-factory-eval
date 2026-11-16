# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T03:58:41+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T03:59:29+00:00 | snapshot-check | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-16T04:03:10+00:00 | delivery-invariant-red | 1 | 2.91 | `pytest -q tests/data_migration/test_invariants.py` | `47f8a3a87f5f9898` | E           TypeError: A handling activity requires a location |  |
| 2026-11-16T04:03:52+00:00 | invariants-green | 0 | 1.22 | `pytest -q tests/data_migration/test_invariants.py` | `48b13902e11e2ab0` |  |  |
| 2026-11-16T04:04:23+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `2ff4ac980449d26f` | Found 1 error. |  |
| 2026-11-16T04:04:33+00:00 | idiom-ruff-check-rerun | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T04:04:33+00:00 | idiom-format-check | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-16T04:04:33+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T04:04:33+00:00 | build-check | 0 | 0.22 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T04:05:07+00:00 | behavior | 0 | 28.48 | `pytest -q` | `12c08ed44517e93f` |  |  |
| 2026-11-16T04:05:35+00:00 | regression | 0 | 27.9 | `pytest -q` | `4fb3c3b464909716` |  |  |
| 2026-11-16T04:06:08+00:00 | crap-coverage | 0 | 27.29 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `cadebc127f596faf` |  |  |
| 2026-11-16T04:06:08+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T04:06:08+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-16T04:06:13+00:00 | mutation-changed | 0 | 0.06 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
