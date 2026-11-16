# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T05:55:04+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T05:56:33+00:00 | fixture-snapshot-check | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-16T05:58:44+00:00 | invariants-focused | 0 | 3.13 | `pytest -q tests/data_migration/test_invariants.py` | `aad2405d7cd17123` |  |  |
| 2026-11-16T05:59:13+00:00 | invariants-focused-final | 0 | 1.28 | `pytest -q tests/data_migration/test_invariants.py` | `6d62fa340acc13b4` |  |  |
| 2026-11-16T05:59:57+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T06:00:00+00:00 | build-check | 0 | 0.25 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T06:00:33+00:00 | behavior | 0 | 31.06 | `pytest -q` | `4f69677693c0afd8` |  |  |
| 2026-11-16T06:00:36+00:00 | idiom-lint | 1 | 0.02 | `ruff check` | `2cf85c453129f131` | 190 \|             assert movement.departure_time < movement.arrival_time |  |
| 2026-11-16T06:00:45+00:00 | idiom-lint-rerun | 1 | 0.01 | `ruff check` | `3ef83ff74f3405f2` | Found 1 error. |  |
| 2026-11-16T06:00:51+00:00 | idiom-lint-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T06:00:55+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-16T06:00:59+00:00 | invariants-after-lint | 0 | 1.28 | `pytest -q tests/data_migration/test_invariants.py` | `6d62fa340acc13b4` |  |  |
| 2026-11-16T06:01:31+00:00 | crap-coverage | 0 | 29.02 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `c23a6432ca072c16` |  |  |
| 2026-11-16T06:01:34+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T06:01:38+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-16T06:01:41+00:00 | mutation-changed | 0 | 0.07 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-16T06:02:22+00:00 | regression | 0 | 33.53 | `pytest -q` | `7485ec50da1bccda` |  |  |
