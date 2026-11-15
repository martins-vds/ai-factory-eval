# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T23:45:13+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T23:48:36+00:00 | invariants-red | 1 | 4.13 | `pytest -q tests/data_migration/test_invariants.py` | `6b98c95884586e1a` | E               psycopg.errors.ForeignKeyViolation: insert or update on table "HandlingEvent" violates foreign key const |  |
| 2026-11-15T23:48:53+00:00 | invariants-red-rerun | 0 | 2.11 | `pytest -q tests/data_migration/test_invariants.py` | `578cebb7a3c297c1` |  |  |
| 2026-11-15T23:49:24+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T23:49:25+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T23:50:19+00:00 | behavior | 0 | 50.59 | `pytest -q` | `0ef2bd3530d4a90f` |  |  |
| 2026-11-15T23:50:22+00:00 | idiom-ruff-check | 1 | 0.03 | `ruff check` | `3b51a23bcb82a689` | 142 \|         assert all( |  |
| 2026-11-15T23:50:32+00:00 | invariants-final | 0 | 2.12 | `pytest -q tests/data_migration/test_invariants.py` | `8a5170c47238fc99` |  |  |
| 2026-11-15T23:50:32+00:00 | idiom-ruff-check-rerun | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T23:50:32+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `82ec9e690f9ee782` |  |  |
| 2026-11-15T23:51:04+00:00 | invariants-formatted | 0 | 2.1 | `pytest -q tests/data_migration/test_invariants.py` | `10e96b85b3bd96cf` |  |  |
| 2026-11-15T23:51:04+00:00 | format-changed-file | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-15T23:52:36+00:00 | regression | 0 | 50.15 | `pytest -q` | `397b3f8d80dbbec1` |  |  |
| 2026-11-15T23:53:29+00:00 | crap-coverage | 0 | 47.88 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `1c3331fcd6e2ca32` |  |  |
| 2026-11-15T23:53:29+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T23:53:29+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-15T23:53:34+00:00 | mutation-changed | 0 | 0.08 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
