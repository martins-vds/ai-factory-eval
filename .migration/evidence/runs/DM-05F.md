# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-20T00:34:40+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:35:59+00:00 | snapshot-check | 0 | 0.04 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-20T00:38:20+00:00 | delivery-invariant-red | 0 | 1.48 | `pytest -q tests/data_migration/test_invariants.py::test_loaded_cargo_delivery_state_matches_its_handling_history` | `ab19f6473f2f72d9` |  |  |
| 2026-11-20T00:39:12+00:00 | invariants-tests | 0 | 1.37 | `pytest -q tests/data_migration/test_invariants.py` | `b72ff9de67279024` |  |  |
| 2026-11-20T00:39:54+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:39:54+00:00 | build-check | 0 | 0.26 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T00:39:54+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `4c74f524bdbc921e` |  |  |
| 2026-11-20T00:40:27+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:40:27+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `76aa0a776e7b042c` |  |  |
| 2026-11-20T00:40:36+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-20T00:40:36+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:40:38+00:00 | invariants-tests-final | 0 | 1.31 | `pytest -q tests/data_migration/test_invariants.py` | `cb1a715d9942259c` |  |  |
| 2026-11-20T00:41:17+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:41:17+00:00 | build-check | 0 | 0.25 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T00:41:17+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:41:17+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-20T00:41:17+00:00 | idiom-layers | 0 | 0.09 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-20T00:41:18+00:00 | idiom-ui | 0 | 0.35 | `python .migration/harness/tools/check_ui.py` | `8f47a220c77d88b6` |  | gate=ui scope="templates changed since 15061bf33fd80017add31ddbaffd35a71289189c" templates=0 findings=0 |
| 2026-11-20T00:41:53+00:00 | behavior | 0 | 29.51 | `pytest -q` | `c536e18de3e0e317` |  |  |
| 2026-11-20T00:42:28+00:00 | crap-coverage | 0 | 27.46 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `89a9e8f2ffd039bf` |  |  |
| 2026-11-20T00:42:28+00:00 | crap-lizard | 0 | 0.08 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:42:28+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-20T00:42:34+00:00 | mutation-changed | 0 | 0.05 | `python .migration/harness/tools/afs-mutation` | `1568e5773417b4bf` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=15061bf33fd80017add31ddbaffd35a71289189c |
| 2026-11-20T00:44:12+00:00 | migration-validate | 1 | 2.89 | `python .migration/harness/tools/validate.py .migration` | `ec9b92c98b3bb1da` | 184 file(s) checked, 1 error(s) |  |
| 2026-11-20T00:44:49+00:00 | migration-validate | 0 | 2.85 | `python .migration/harness/tools/validate.py .migration` | `b05e2a864e5153ee` |  |  |
