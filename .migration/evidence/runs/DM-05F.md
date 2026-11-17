# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-17T21:42:29+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:45:14+00:00 | invariants | 0 | 4.08 | `pytest -q tests/data_migration/test_invariants.py` | `8a5170c47238fc99` |  |  |
| 2026-11-17T21:45:40+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:45:44+00:00 | build-check | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-17T21:45:46+00:00 | idiom-lint | 1 | 0.02 | `ruff check` | `31955aadf9a34987` | 171 \|         assert all( |  |
| 2026-11-17T21:46:09+00:00 | invariants-after-lint-fix | 0 | 1.62 | `pytest -q tests/data_migration/test_invariants.py` | `7bbfa9adac667373` |  |  |
| 2026-11-17T21:46:12+00:00 | idiom-lint-final | 1 | 0.01 | `ruff check` | `1d3ce8f044cb4e78` | Found 1 error. |  |
| 2026-11-17T21:46:17+00:00 | idiom-autofix | 0 | 0.01 | `ruff check --fix tests/data_migration/test_invariants.py` | `aac3a0503d8b9505` | Found 1 error (1 fixed, 0 remaining). |  |
| 2026-11-17T21:46:20+00:00 | idiom-lint-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:46:22+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-17T21:47:13+00:00 | crap-coverage | 0 | 36.71 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `0408962aa5bff26c` |  |  |
| 2026-11-17T21:47:16+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:47:19+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-17T21:47:23+00:00 | mutation-changed | 0 | 0.07 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-17T21:48:11+00:00 | regression | 0 | 36.54 | `pytest -q` | `b0af01e18c998da0` |  |  |
