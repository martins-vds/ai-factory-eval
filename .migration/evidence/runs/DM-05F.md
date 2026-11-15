# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T20:11:58+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T20:16:01+00:00 | invariants-red | 1 | 1.4 | `pytest -q tests/data_migration/test_invariants.py` | `0c048e4ad2f6076c` | E           TypeError: A handling activity requires a location |  |
| 2026-11-15T20:16:33+00:00 | invariants-focused | 0 | 1.14 | `pytest -q tests/data_migration/test_invariants.py` | `0a4c969597b9223e` |  |  |
| 2026-11-15T20:16:56+00:00 | snapshot-check | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-15T20:17:04+00:00 | format-targeted | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-15T20:17:04+00:00 | idiom-targeted | 1 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `c0185429e6070c5c` | 143 \|         assert len(legs) >= 2 |  |
| 2026-11-15T20:17:20+00:00 | idiom-targeted-rerun | 0 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T20:17:20+00:00 | format-targeted-rerun | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-15T20:17:21+00:00 | invariants-focused-rerun | 0 | 1.17 | `pytest -q tests/data_migration/test_invariants.py` | `c2af2bda05262d37` |  |  |
| 2026-11-15T20:17:29+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T20:17:33+00:00 | build-check | 0 | 0.22 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T20:18:06+00:00 | behavior | 0 | 28.76 | `pytest -q` | `6d1c4b08d2463a91` |  |  |
| 2026-11-15T20:18:09+00:00 | idiom | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T20:18:12+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `1e2a3e2494e870c6` |  |  |
| 2026-11-15T20:18:43+00:00 | crap-coverage | 0 | 26.03 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `b4c4634528bb31b5` |  |  |
| 2026-11-15T20:18:47+00:00 | crap-lizard | 0 | 0.08 | `sh -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T20:18:51+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-15T20:19:25+00:00 | regression | 0 | 29.88 | `pytest -q` | `ccd837a32ae326c8` |  |  |
| 2026-11-15T20:19:29+00:00 | mutation-changed | 0 | 0.05 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
