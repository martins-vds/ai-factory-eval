# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T03:06:52+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:09:32+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot tests/data_migration/fixtures/DM-05C` | `525bd2128fe2515f` |  | gate=data-snapshot tables=6 problems=0 |
| 2026-11-18T03:11:17+00:00 | invariants-red | 1 | 4.2 | `pytest -q tests/data_migration/test_invariants.py` | `0a7d0bcd225ba1e9` | E       TypeError: TempPathFactory.__init__() missing 4 required positional arguments: 'given_basetemp', 'retention_coun |  |
| 2026-11-18T03:11:26+00:00 | invariants | 0 | 2.11 | `pytest -q tests/data_migration/test_invariants.py` | `578cebb7a3c297c1` |  |  |
| 2026-11-18T03:12:13+00:00 | idiom-ruff | 1 | 0.03 | `ruff check` | `bdb8ee94ebe8ba12` | 149 \|         assert all( |  |
| 2026-11-18T03:12:33+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T03:12:38+00:00 | invariants | 0 | 2.12 | `pytest -q tests/data_migration/test_invariants.py` | `10e96b85b3bd96cf` |  |  |
| 2026-11-18T03:13:07+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `7b29ac69e6f91463` | 162 \|     assert all(event.location_id in location_ids for event in events) |  |
| 2026-11-18T03:13:15+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T03:13:19+00:00 | build-compileall | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:13:22+00:00 | build-django-check | 0 | 0.37 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T03:13:24+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T03:13:27+00:00 | idiom-layers | 0 | 0.15 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T03:13:30+00:00 | idiom-ui | 0 | 0.51 | `python .migration/harness/tools/check_ui.py` | `e63800adfc6f1bf5` |  | gate=ui scope="templates changed since 22d48f3b9f317575446703e3a2f723abf53ff26d" templates=0 findings=0 |
| 2026-11-18T03:14:36+00:00 | crap-coverage | 0 | 59.98 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `08f930bcadbaef63` |  |  |
| 2026-11-18T03:14:39+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T03:14:42+00:00 | crap-report | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-18T03:14:46+00:00 | mutation-changed | 0 | 0.08 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-18T03:15:39+00:00 | regression | 0 | 48.62 | `pytest -q` | `d2406a739fa9a9b6` |  |  |
