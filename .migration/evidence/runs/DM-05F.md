# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-17T21:05:16+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:09:41+00:00 | behavior | 0 | 3.83 | `pytest -q tests/data_migration/test_invariants.py` | `d3db388f4ecc4e6b` |  |  |
| 2026-11-17T21:10:10+00:00 | idiom-lint | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:10:14+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-17T21:10:39+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:10:42+00:00 | build-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-17T21:11:23+00:00 | regression | 0 | 38.45 | `pytest -q` | `c2b4d6157e3ec044` |  |  |
| 2026-11-17T21:12:04+00:00 | crap-tests | 0 | 34.29 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `558f1bc5ae45933b` |  |  |
| 2026-11-17T21:12:07+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:12:10+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-17T21:12:16+00:00 | mutation-changed | 0 | 0.06 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-17T21:17:37+00:00 | behavior-review-fix | 0 | 1.6 | `pytest -q tests/data_migration/test_invariants.py` | `01b439f99d953570` |  |  |
| 2026-11-17T21:17:42+00:00 | idiom-lint-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:17:45+00:00 | idiom-format-final | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-17T21:18:24+00:00 | regression-final | 0 | 34.46 | `pytest -q` | `fe4b64c3760415df` |  |  |
| 2026-11-17T21:19:03+00:00 | crap-tests-final | 0 | 35.89 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `ab62ab1f3d9524ca` |  |  |
| 2026-11-17T21:19:07+00:00 | crap-lizard-final | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:19:10+00:00 | crap-score-final | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
