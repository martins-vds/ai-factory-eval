# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T06:09:05+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T06:13:05+00:00 | fixture-snapshot-check | 0 | 0.07 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-15T06:14:14+00:00 | delivery-invariant | 0 | 3.89 | `pytest -q tests/data_migration/test_invariants.py` | `483bd3660ffb0fe6` |  |  |
| 2026-11-15T06:15:15+00:00 | delivery-itinerary-invariants | 0 | 2.04 | `pytest -q tests/data_migration/test_invariants.py` | `c00baeaf11bd9e48` |  |  |
| 2026-11-15T06:15:42+00:00 | loaded-business-invariants | 0 | 2.16 | `pytest -q tests/data_migration/test_invariants.py` | `f56eadf3d7746ccb` |  |  |
| 2026-11-15T06:16:05+00:00 | idiom-ruff-check | 1 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `19d7f8203a522dba` | 168 \|         assert all( |  |
| 2026-11-15T06:16:16+00:00 | idiom-ruff-check-rerun | 0 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T06:16:19+00:00 | idiom-format-check | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-15T06:16:25+00:00 | loaded-business-invariants-rerun | 0 | 2.12 | `pytest -q tests/data_migration/test_invariants.py` | `d54dcac94e4b7fc8` |  |  |
| 2026-11-15T06:16:46+00:00 | loaded-business-invariants-final | 0 | 2.04 | `pytest -q tests/data_migration/test_invariants.py` | `af038f625faaaee2` |  |  |
| 2026-11-15T06:17:13+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T06:17:17+00:00 | build-django-check | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T06:17:21+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T06:17:25+00:00 | idiom-format-check | 0 | 0.02 | `ruff format --check` | `1e2a3e2494e870c6` |  |  |
| 2026-11-15T06:18:21+00:00 | behavior-regression | 0 | 51.86 | `pytest -q` | `36126d827daea4fc` |  |  |
| 2026-11-15T06:19:24+00:00 | crap-coverage | 0 | 59.32 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `58eb21813c731162` |  |  |
| 2026-11-15T06:19:30+00:00 | crap-lizard | 0 | 0.16 | `sh -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T06:19:34+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
