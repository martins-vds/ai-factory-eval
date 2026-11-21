# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T18:59:38+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T19:02:54+00:00 | delivery-invariant-red | 1 | 2.39 | `pytest -q tests/data_migration/test_invariants.py` | `7f90152f3fc1a26f` | E           TypeError: A handling activity requires a location |  |
| 2026-11-21T19:03:35+00:00 | invariants-targeted | 0 | 2.28 | `pytest -q tests/data_migration/test_invariants.py` | `624e8ca77d788c89` |  |  |
| 2026-11-21T19:04:03+00:00 | invariants-red-green | 0 | 2.26 | `pytest -q tests/data_migration/test_invariants.py` | `4dc6033adb5540b5` |  |  |
| 2026-11-21T19:04:32+00:00 | data-migration-tests | 0 | 6.21 | `pytest -q tests/data_migration` | `f2a7af5dd6023948` |  |  |
| 2026-11-21T19:04:47+00:00 | ruff-check | 1 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `e48e7cba78b55cfe` |  |  |
| 2026-11-21T19:04:54+00:00 | ruff-check | 0 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T19:04:54+00:00 | ruff-format | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-21T19:04:54+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T19:04:54+00:00 | build-check | 0 | 0.4 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T19:05:25+00:00 | snapshot-fixture-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-21T19:05:57+00:00 | final-build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T19:05:57+00:00 | final-build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T19:05:57+00:00 | final-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T19:05:57+00:00 | final-ruff-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-21T19:05:58+00:00 | final-check-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T19:05:58+00:00 | final-check-ui | 0 | 0.64 | `python .migration/harness/tools/check_ui.py` | `aeae76814f7bb1a8` |  | gate=ui scope="templates changed since 195ceb4a4d45084ee3e573f7eb91433ed305d944" templates=0 findings=0 |
| 2026-11-21T19:06:49+00:00 | final-crap-coverage | 0 | 50.3 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `aa940de47007f801` |  |  |
| 2026-11-21T19:06:49+00:00 | final-crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T19:06:49+00:00 | final-crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-21T19:06:49+00:00 | final-mutation-changed | 0 | 0.09 | `python .migration/harness/tools/afs-mutation` | `0ad19ea9060735ec` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=195ceb4a4d45084ee3e573f7eb91433ed305d944 |
| 2026-11-21T19:07:39+00:00 | final-regression | 0 | 50.32 | `pytest -q` | `fa0bdf159b3c4c92` |  |  |
| 2026-11-21T19:09:28+00:00 | final-validate | 1 | 4.95 | `python .migration/harness/tools/validate.py .migration` | `ec9b92c98b3bb1da` | 184 file(s) checked, 1 error(s) |  |
| 2026-11-21T19:09:57+00:00 | final-validate | 0 | 4.99 | `python .migration/harness/tools/validate.py .migration` | `b05e2a864e5153ee` |  |  |
