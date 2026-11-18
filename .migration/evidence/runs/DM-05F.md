# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T12:33:05+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:38:20+00:00 | targeted-tests | 0 | 3.62 | `pytest -q tests/data_migration/test_invariants.py` | `df589a78f8a8b32b` |  |  |
| 2026-11-18T12:38:45+00:00 | targeted-tests | 0 | 2.15 | `pytest -q tests/data_migration/test_invariants.py` | `8a5170c47238fc99` |  |  |
| 2026-11-18T12:39:20+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:39:20+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T12:39:20+00:00 | idiom-ruff | 1 | 0.03 | `ruff check` | `0dfb65272ac2879e` | 163 \|         assert all( |  |
| 2026-11-18T12:39:21+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `e83a00b6452d19f1` | 146 \|         assert cargo.delivery.misdirected == derived.misdirected |  |
| 2026-11-18T12:39:21+00:00 | idiom-layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T12:39:21+00:00 | idiom-ui | 0 | 0.5 | `python .migration/harness/tools/check_ui.py` | `4bb50f56ce3cb94f` |  | gate=ui scope="templates changed since eb1a34bde78d1032d64b46b30e4fe650290f317f" templates=0 findings=0 |
| 2026-11-18T12:39:37+00:00 | targeted-tests | 0 | 2.14 | `pytest -q tests/data_migration/test_invariants.py` | `8a5170c47238fc99` |  |  |
| 2026-11-18T12:39:37+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:39:37+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T12:40:51+00:00 | crap-coverage | 0 | 48.74 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `c14475cf26c2ab5e` |  |  |
| 2026-11-18T12:40:51+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:40:52+00:00 | crap-report | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-18T12:40:55+00:00 | mutation-changed | 0 | 0.09 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-18T12:41:16+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:41:17+00:00 | build-check | 0 | 0.39 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T12:41:17+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:41:17+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T12:41:17+00:00 | idiom-layers | 0 | 0.15 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T12:41:18+00:00 | idiom-ui | 0 | 0.5 | `python .migration/harness/tools/check_ui.py` | `4bb50f56ce3cb94f` |  | gate=ui scope="templates changed since eb1a34bde78d1032d64b46b30e4fe650290f317f" templates=0 findings=0 |
| 2026-11-18T12:42:07+00:00 | behavior | 0 | 48.76 | `pytest -q` | `dd4a943e58f89252` |  |  |
| 2026-11-18T12:44:52+00:00 | regression | 0 | 48.25 | `pytest -q` | `5a45dbf3a92c3668` |  |  |
| 2026-11-18T12:47:33+00:00 | targeted-tests | 0 | 2.2 | `pytest -q tests/data_migration/test_invariants.py` | `4dc6033adb5540b5` |  |  |
| 2026-11-18T12:47:33+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T12:47:33+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T12:47:40+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:47:41+00:00 | build-check | 0 | 0.4 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T12:47:41+00:00 | idiom-layers | 0 | 0.15 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T12:47:41+00:00 | idiom-ui | 0 | 0.52 | `python .migration/harness/tools/check_ui.py` | `4bb50f56ce3cb94f` |  | gate=ui scope="templates changed since eb1a34bde78d1032d64b46b30e4fe650290f317f" templates=0 findings=0 |
| 2026-11-18T12:48:36+00:00 | crap-coverage | 0 | 49.12 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `700e9dcb6058ed42` |  |  |
| 2026-11-18T12:48:37+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T12:48:37+00:00 | crap-report | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-18T13:04:25+00:00 | behavior | 0 | 47.14 | `pytest -q` | `a82b0444afc8953f` |  |  |
| 2026-11-18T13:05:32+00:00 | regression | 0 | 48.55 | `pytest -q` | `03da98cea7b5bf95` |  |  |
| 2026-11-18T13:08:55+00:00 | targeted-tests | 0 | 2.16 | `pytest -q tests/data_migration/test_invariants.py` | `2f3f135b0c3dde0e` |  |  |
| 2026-11-18T13:08:56+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T13:08:56+00:00 | idiom-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-18T13:09:01+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:09:02+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T13:09:02+00:00 | idiom-layers | 0 | 0.15 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T13:09:02+00:00 | idiom-ui | 0 | 0.54 | `python .migration/harness/tools/check_ui.py` | `4bb50f56ce3cb94f` |  | gate=ui scope="templates changed since eb1a34bde78d1032d64b46b30e4fe650290f317f" templates=0 findings=0 |
| 2026-11-18T13:10:07+00:00 | crap-coverage | 0 | 57.79 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `0d51c8842525a1d6` |  |  |
| 2026-11-18T13:10:08+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T13:10:08+00:00 | crap-report | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-18T13:10:57+00:00 | behavior | 0 | 49.31 | `pytest -q` | `518edc79ceaef887` |  |  |
| 2026-11-18T13:11:45+00:00 | regression | 0 | 47.21 | `pytest -q` | `05f04b74015cef79` |  |  |
| 2026-11-18T13:15:22+00:00 | regression | 0 | 47.87 | `pytest -q` | `ac082027ee84ceb4` |  |  |
