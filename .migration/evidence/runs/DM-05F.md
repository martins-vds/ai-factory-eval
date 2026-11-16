# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-16T13:32:56+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T13:35:49+00:00 | data-snapshot | 0 | 0.05 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-16T13:37:06+00:00 | invariants-delivery | 1 | 4.92 | `pytest -q tests/data_migration/test_invariants.py` | `3ca06a0aa1093202` | >           assert cargo.delivery == replace(expected, last_event_id=history.most_recent_event_id) |  |
| 2026-11-16T13:37:26+00:00 | invariants-delivery | 0 | 1.66 | `pytest -q tests/data_migration/test_invariants.py` | `7bc5776d19eed069` |  |  |
| 2026-11-16T13:37:45+00:00 | invariants | 0 | 2.17 | `pytest -q tests/data_migration/test_invariants.py` | `578cebb7a3c297c1` |  |  |
| 2026-11-16T13:38:03+00:00 | idiom-ruff-check | 1 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `76037f3e14f4be29` | 184 \|         assert all( |  |
| 2026-11-16T13:38:13+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check tests/data_migration/test_invariants.py` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T13:38:13+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check tests/data_migration/test_invariants.py` | `fd2299c9f1c6dc86` |  |  |
| 2026-11-16T13:38:39+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T13:38:40+00:00 | build-django-check | 0 | 0.34 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-16T13:38:42+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-16T13:38:43+00:00 | idiom-ruff-format | 0 | 0.02 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-16T13:39:26+00:00 | behavior | 0 | 40.71 | `pytest -q` | `257af09ef1201bd2` |  |  |
| 2026-11-16T13:40:25+00:00 | regression | 0 | 39.73 | `pytest -q` | `3df747691e77f899` |  |  |
| 2026-11-16T13:41:10+00:00 | crap-coverage | 0 | 40.98 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `222a31ed4bde39d0` |  |  |
| 2026-11-16T13:41:14+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T13:41:14+00:00 | crap-threshold | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-16T13:41:18+00:00 | mutation-changed | 0 | 0.06 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
