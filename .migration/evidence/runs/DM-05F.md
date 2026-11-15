# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T17:47:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T17:52:29+00:00 | invariants | 0 | 4.18 | `pytest -q tests/data_migration/test_invariants.py` | `99b46a9054cdd02b` |  |  |
| 2026-11-15T17:53:06+00:00 | idiom-focused | 1 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `a2d5ec536e477239` | 100 \|         assert all( |  |
| 2026-11-15T17:53:24+00:00 | idiom-focused | 0 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T17:53:24+00:00 | format-focused | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-15T17:53:27+00:00 | invariants | 0 | 2.21 | `pytest -q tests/data_migration/test_invariants.py` | `8a5170c47238fc99` |  |  |
| 2026-11-15T17:53:56+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T17:54:00+00:00 | build-check | 0 | 0.42 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T17:55:06+00:00 | behavior | 0 | 61.63 | `pytest -q` | `09f16ad39808ecd3` |  |  |
| 2026-11-15T17:55:11+00:00 | idiom-lint | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T17:55:11+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `1e2a3e2494e870c6` |  |  |
| 2026-11-15T17:56:06+00:00 | crap-pytest | 0 | 49.33 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `7c5476c46fc82122` |  |  |
| 2026-11-15T17:56:07+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T17:56:07+00:00 | crap-check | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-15T17:57:02+00:00 | regression | 0 | 49.36 | `pytest -q` | `a26840407d0e2d44` |  |  |
| 2026-11-15T17:57:06+00:00 | mutation-changed | 0 | 0.09 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-15T17:57:57+00:00 | invariants-final | 0 | 2.13 | `pytest -q tests/data_migration/test_invariants.py` | `10e96b85b3bd96cf` |  |  |
| 2026-11-15T17:57:57+00:00 | idiom-focused | 0 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T17:57:57+00:00 | format-focused | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
