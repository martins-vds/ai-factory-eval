# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T13:42:45+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T13:44:37+00:00 | invariants-focused | 1 | 2.51 | `pytest -q tests/data_migration/test_invariants.py` | `1df56ec50d90abff` | E           TypeError: A handling activity requires a location |  |
| 2026-11-15T13:46:00+00:00 | invariants-focused | 0 | 2.18 | `pytest -q tests/data_migration/test_invariants.py` | `578cebb7a3c297c1` |  |  |
| 2026-11-15T13:46:45+00:00 | idiom-format | 0 | 0.08 | `ruff format --check` | `1e2a3e2494e870c6` |  |  |
| 2026-11-15T13:46:45+00:00 | idiom-ruff | 1 | 0.06 | `ruff check` | `0c0c885564515ad1` | 173 \|         assert all( |  |
| 2026-11-15T13:46:45+00:00 | build-compile | 0 | 0.16 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T13:46:45+00:00 | snapshot-check | 0 | 0.1 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-15T13:46:46+00:00 | build-check | 0 | 0.5 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T13:46:58+00:00 | idiom-ruff-rerun | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T13:47:00+00:00 | invariants-focused-rerun | 0 | 2.15 | `pytest -q tests/data_migration/test_invariants.py` | `578cebb7a3c297c1` |  |  |
| 2026-11-15T13:47:57+00:00 | behavior | 0 | 52.91 | `pytest -q` | `80c0581233dd534f` |  |  |
| 2026-11-15T13:48:52+00:00 | crap | 0 | 49.78 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `9b1e6684674e5a53` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-15T14:24:59+00:00 | regression | 0 | 57.99 | `pytest -q` | `0d124f3922bde1cb` |  |  |
| 2026-11-15T14:35:35+00:00 | mutation-changed | 2 | 2797.67 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `ba68236077aa8b8d` | afs-mutation: mutmut failed on src/cargotracker/data_migration/loader.py; its mutants were not tested: | gate=mutation score=n/a error=mutmut-failed failed_files=6 files=75 base=origin/main |
