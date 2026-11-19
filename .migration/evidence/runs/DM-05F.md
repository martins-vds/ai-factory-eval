# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T18:17:30+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:18:02+00:00 | snapshot-validation | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-19T18:21:12+00:00 | invariants-delivery | 0 | 4.01 | `pytest -q tests/data_migration/test_invariants.py` | `1c6b0233fa8cd732` |  |  |
| 2026-11-19T18:21:39+00:00 | invariants-delivery | 0 | 1.67 | `pytest -q tests/data_migration/test_invariants.py` | `941ba30613647e4a` |  |  |
| 2026-11-19T18:22:07+00:00 | invariants | 0 | 1.92 | `pytest -q tests/data_migration/test_invariants.py` | `bb19e66110651773` |  |  |
| 2026-11-19T18:22:42+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:22:42+00:00 | build-check | 0 | 0.35 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T18:22:46+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `79acecc9eb6f220a` | Found 1 error. |  |
| 2026-11-19T18:22:53+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:22:53+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `16f8135ecb528083` | -         assert any(len(legs) > 1 for legs in itineraries) |  |
| 2026-11-19T18:23:04+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:23:04+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-19T18:23:06+00:00 | invariants | 0 | 1.92 | `pytest -q tests/data_migration/test_invariants.py` | `846f06875c7c84ed` |  |  |
| 2026-11-19T18:23:23+00:00 | idiom-layers | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T18:23:24+00:00 | idiom-ui | 0 | 0.42 | `python .migration/harness/tools/check_ui.py` | `729dd387bb9e8c9e` |  | gate=ui scope="templates changed since dc8bf5bdad0c38bd5c1ea80e544f35bff42dc367" templates=0 findings=0 |
| 2026-11-19T18:24:16+00:00 | regression | 0 | 46.79 | `pytest -q` | `c4a951283d743712` |  |  |
| 2026-11-19T18:25:04+00:00 | crap-coverage | 0 | 43.56 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov'` | `7f45bc97aae7e681` |  |  |
| 2026-11-19T18:25:08+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:25:08+00:00 | crap-analysis | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-19T18:25:11+00:00 | mutation-changed | 0 | 0.08 | `python .migration/harness/tools/afs-mutation` | `145d21563a3c707f` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=dc8bf5bdad0c38bd5c1ea80e544f35bff42dc367 |
