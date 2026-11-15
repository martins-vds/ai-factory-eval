# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T02:39:02+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T02:43:58+00:00 | invariants | 0 | 3.94 | `pytest -q tests/data_migration/test_invariants.py` | `c891f7c156cefdaf` |  |  |
| 2026-11-15T02:44:16+00:00 | idiom-check | 1 | 0.02 | `ruff check` | `8358f95e76afb548` | 160 \|         assert all( |  |
| 2026-11-15T02:44:28+00:00 | idiom-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T02:44:28+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `9413a24632f5b0cc` | 147 \|         assert stored.misdirected == derived.misdirected |  |
| 2026-11-15T02:45:03+00:00 | invariants | 0 | 1.59 | `pytest -q tests/data_migration/test_invariants.py` | `43885598a71d1469` |  |  |
| 2026-11-15T02:45:03+00:00 | idiom-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T02:45:03+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `1e2a3e2494e870c6` |  |  |
| 2026-11-15T02:45:41+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T02:45:41+00:00 | build-check | 0 | 0.28 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T02:46:17+00:00 | behavior | 0 | 35.83 | `pytest -q` | `bb17b4d954e0e23b` |  |  |
| 2026-11-15T02:46:53+00:00 | regression | 0 | 36.26 | `pytest -q` | `40581f18e83c6895` |  |  |
| 2026-11-15T02:47:41+00:00 | crap-coverage | 0 | 36.74 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `42e187b89ef8d5d4` |  |  |
| 2026-11-15T02:47:41+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T02:47:41+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-15T03:20:54+00:00 | mutation-changed | 2 | 1988.97 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `12a15fea8ac7e76c` | afs-mutation: mutmut failed on src/cargotracker/data_migration/loader.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=6 files=75 base=origin/main |
| 2026-11-15T03:21:45+00:00 | invariants | 0 | 1.64 | `pytest -q tests/data_migration/test_invariants.py` | `14966a85db57e41f` |  |  |
| 2026-11-15T03:21:45+00:00 | idiom-check | 1 | 0.01 | `ruff check` | `77b7f984d02b407c` | Found 1 error. |  |
| 2026-11-15T03:22:09+00:00 | invariants | 0 | 1.65 | `pytest -q tests/data_migration/test_invariants.py` | `e3bc99a1d6726a8f` |  |  |
| 2026-11-15T03:22:09+00:00 | idiom-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T03:22:09+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `1e2a3e2494e870c6` |  |  |
| 2026-11-15T03:22:44+00:00 | regression | 0 | 35.07 | `pytest -q` | `9d0dc6c409ae1016` |  |  |
