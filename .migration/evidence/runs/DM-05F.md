# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T01:35:03+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:38:31+00:00 | invariants | 0 | 2.9 | `pytest -q tests/data_migration/test_invariants.py` | `7ed2738ac3dcd8f9` |  |  |
| 2026-11-23T01:38:48+00:00 | idiom-ruff | 1 | 0.02 | `ruff check` | `938d9cea43029b50` | 165 \|         assert all( |  |
| 2026-11-23T01:38:55+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T01:38:58+00:00 | invariants | 0 | 1.26 | `pytest -q tests/data_migration/test_invariants.py` | `db3aca357b581d38` |  |  |
| 2026-11-23T01:39:02+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `fe1a57e6ce5df523` | 138 \|     assert cargo is not None |  |
| 2026-11-23T01:39:08+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T01:39:11+00:00 | invariants | 0 | 1.19 | `pytest -q tests/data_migration/test_invariants.py` | `db3aca357b581d38` |  |  |
| 2026-11-23T01:39:35+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:39:38+00:00 | build-check | 0 | 0.33 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T01:39:40+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T01:39:43+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T01:39:45+00:00 | idiom-layers | 0 | 0.1 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-23T01:39:48+00:00 | idiom-ui | 0 | 0.41 | `python .migration/harness/tools/check_ui.py` | `b5a62b5292fc8c6b` |  | gate=ui scope="templates changed since 46d4d47ef6c7b2e326324a52d1406a9393fae7a3" templates=0 findings=0 |
| 2026-11-23T01:40:21+00:00 | regression | 0 | 30.05 | `pytest -q` | `167f7ad5592fa47e` |  |  |
| 2026-11-23T01:40:54+00:00 | crap-pytest | 0 | 29.94 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `1e5876aa518c3202` |  |  |
| 2026-11-23T01:40:57+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:41:00+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-23T01:41:03+00:00 | mutation-changed | 0 | 0.06 | `python .migration/harness/tools/afs-mutation` | `4abed1a9cf2b42c2` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=46d4d47ef6c7b2e326324a52d1406a9393fae7a3 |
