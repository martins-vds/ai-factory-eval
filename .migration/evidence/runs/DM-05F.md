# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T20:51:05+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:53:10+00:00 | snapshot-check | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-16T20:55:21+00:00 | invariants | 1 | 4.45 | `pytest -q tests/data_migration/test_invariants.py` | `70e2e3c714accc90` | assert len(cargos) == 2 |  |
| 2026-11-16T20:55:34+00:00 | invariants | 0 | 1.71 | `pytest -q tests/data_migration/test_invariants.py` | `c22487a850faaa14` |  |  |
| 2026-11-16T20:55:53+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:55:58+00:00 | build-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T20:56:01+00:00 | idiom-ruff | 1 | 0.02 | `ruff check` | `be72b09a36d0f194` | 275 \|         assert all( |  |
| 2026-11-16T20:56:14+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T20:56:17+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `d536b87e7f4a58d1` | -         assert replace(derived_delivery, last_event_id=history.most_recent_event_id) == cargo.delivery |  |
| 2026-11-16T20:56:24+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-16T20:57:05+00:00 | regression | 0 | 37.36 | `pytest -q` | `316e4afbb753fbdd` |  |  |
| 2026-11-16T20:57:47+00:00 | crap-coverage | 0 | 36.8 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `c7ffef7c52a2980c` |  |  |
| 2026-11-16T20:57:50+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:57:53+00:00 | crap-threshold | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-16T20:58:05+00:00 | mutation-changed | 0 | 0.07 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-16T20:59:19+00:00 | invariants-final | 0 | 1.65 | `pytest -q tests/data_migration/test_invariants.py` | `9bed9041f3a97041` |  |  |
| 2026-11-16T20:59:23+00:00 | idiom-ruff-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T20:59:25+00:00 | idiom-format-final | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-16T21:00:06+00:00 | regression-final | 0 | 37.43 | `pytest -q` | `1d895c0b93c09571` |  |  |
| 2026-11-16T21:00:56+00:00 | crap-coverage-final | 0 | 41.34 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `a0c1d8aa669e7c6b` |  |  |
| 2026-11-16T21:00:59+00:00 | crap-lizard-final | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T21:01:03+00:00 | crap-threshold-final | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-16T21:01:06+00:00 | mutation-changed-final | 0 | 0.06 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
