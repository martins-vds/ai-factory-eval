# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T20:36:35+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:39:25+00:00 | fixture-snapshot | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-16T20:40:44+00:00 | invariants | 1 | 3.37 | `pytest -q tests/data_migration/test_invariants.py` | `e4e74d7943cfdbba` | E           ValueError: Voyage is not allowed with event type RECEIVE |  |
| 2026-11-16T20:41:03+00:00 | invariants | 0 | 1.66 | `pytest -q tests/data_migration/test_invariants.py` | `01b439f99d953570` |  |  |
| 2026-11-16T20:41:49+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:41:53+00:00 | build-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T20:41:57+00:00 | idiom-ruff | 1 | 0.02 | `ruff check` | `783826721e9b72b7` | 187 \|         assert all( |  |
| 2026-11-16T20:42:14+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T20:42:17+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `035cf9fe4f3afe99` |  |  |
| 2026-11-16T20:42:28+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-16T20:42:32+00:00 | invariants | 0 | 1.61 | `pytest -q tests/data_migration/test_invariants.py` | `43885598a71d1469` |  |  |
| 2026-11-16T20:43:26+00:00 | invariants | 0 | 1.68 | `pytest -q tests/data_migration/test_invariants.py` | `9bed9041f3a97041` |  |  |
| 2026-11-16T20:43:29+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T20:43:33+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-16T20:44:41+00:00 | crap-coverage | 0 | 43.53 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `62279c2d26d090f1` |  |  |
| 2026-11-16T20:44:45+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:44:49+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-16T20:44:54+00:00 | mutation-changed | 0 | 0.07 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-16T20:46:09+00:00 | regression | 0 | 40.58 | `pytest -q` | `cf4abf43d2395790` |  |  |
| 2026-11-16T20:48:29+00:00 | invariants | 0 | 1.72 | `pytest -q tests/data_migration/test_invariants.py` | `8ef3627370199135` |  |  |
| 2026-11-16T20:48:32+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T20:48:35+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-16T20:49:00+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:49:08+00:00 | build-check | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T20:49:56+00:00 | crap-coverage | 0 | 43.11 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `c97a2090c420cf1f` |  |  |
| 2026-11-16T20:50:00+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:50:05+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-16T20:50:10+00:00 | mutation-changed | 0 | 0.07 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-16T20:50:53+00:00 | regression | 0 | 40.07 | `pytest -q` | `e64febf83db1360c` |  |  |
| 2026-11-16T20:56:04+00:00 | invariants | 0 | 1.65 | `pytest -q tests/data_migration/test_invariants.py` | `e3bc99a1d6726a8f` |  |  |
| 2026-11-16T20:56:08+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T20:56:12+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-16T20:57:02+00:00 | crap-coverage | 0 | 39.4 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `c8d78b1cb492ad1c` |  |  |
| 2026-11-16T20:57:05+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:57:11+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-16T21:04:56+00:00 | regression | 0 | 42.45 | `pytest -q` | `e595e6cc6669491c` |  |  |
