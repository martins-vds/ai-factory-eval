# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:08:44+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:11:59+00:00 | behavior-red | 2 | 3.58 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8b8e9007a23ad6e9` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-21T13:13:28+00:00 | behavior | 1 | 6.3 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `c207e86817c43635` | assert 'hx-get="/admin/cargo/DEF789/destination/"' in not_routed_table |  |
| 2026-11-21T13:13:46+00:00 | behavior | 0 | 5.89 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `80e6b1ef218f977a` |  |  |
| 2026-11-21T13:13:50+00:00 | lint | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:13:52+00:00 | format-check | 1 | 0.02 | `ruff format --check` | `a54dc92f2f346e41` |  |  |
| 2026-11-21T13:15:12+00:00 | behavior | 0 | 5.66 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `619fa21779391c4f` |  |  |
| 2026-11-21T13:15:15+00:00 | format-check | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T13:15:27+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:15:30+00:00 | build-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T13:15:32+00:00 | layers | 0 | 0.12 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T13:15:35+00:00 | ui | 0 | 0.47 | `python .migration/harness/tools/check_ui.py` | `7c6e08b8dc3096de` |  | gate=ui scope="templates changed since b4373fca788d17c369e8b391a410a0bdde2d5765" templates=4 findings=0 |
| 2026-11-21T13:16:13+00:00 | behavior | 0 | 6.06 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `1d67d03e5efe201b` |  |  |
| 2026-11-21T13:18:58+00:00 | lint | 1 | 0.01 | `ruff check` | `6b9fd418f7b0c2f1` | Found 1 error. |  |
| 2026-11-21T13:19:07+00:00 | lint | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:19:10+00:00 | format-check | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T13:19:18+00:00 | behavior | 0 | 6.12 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `bcca4dc07217a9c1` |  |  |
| 2026-11-21T13:19:21+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:19:24+00:00 | build-check | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T13:19:27+00:00 | layers | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T13:19:30+00:00 | ui | 0 | 0.48 | `python .migration/harness/tools/check_ui.py` | `1d27b2ed2550b112` |  | gate=ui scope="templates changed since b4373fca788d17c369e8b391a410a0bdde2d5765" templates=5 findings=0 |
| 2026-11-21T13:20:22+00:00 | crap-coverage | 0 | 48.11 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `023b316751571e64` |  |  |
| 2026-11-21T13:20:25+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:20:27+00:00 | crap | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `674fe9d8c5797b4c` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-21T13:23:49+00:00 | mutation-changed | 1 | 198.56 | `.migration/harness/tools/afs-mutation` | `d9e82def05b0c09d` | afs-mutation: FAILED score=0.739 threshold=0.8 killed=51 survived=18 skipped=0 files=1 jobs=1 base=b4373fca788d17c369e8b | gate=mutation score=0.739 threshold=0.8 killed=51 survived=18 files=1 base=b4373fca788d17c369e8b391a410a0bdde2d5765 |
| 2026-11-21T13:25:13+00:00 | behavior | 0 | 8.14 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `b0037adc0ca0eca0` |  |  |
| 2026-11-21T13:26:03+00:00 | behavior | 0 | 8.87 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `1eb134a2e5734e53` |  |  |
| 2026-11-21T13:26:07+00:00 | lint | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:26:10+00:00 | format-check | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T13:29:34+00:00 | mutation-changed | 0 | 199.24 | `.migration/harness/tools/afs-mutation` | `2c5716b698c0d64d` |  | gate=mutation score=0.941 threshold=0.8 killed=64 survived=4 files=1 base=b4373fca788d17c369e8b391a410a0bdde2d5765 |
| 2026-11-21T13:31:01+00:00 | behavior | 0 | 8.36 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `c673126945c1b018` |  |  |
| 2026-11-21T13:31:05+00:00 | lint | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-21T13:31:08+00:00 | format-check | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-21T13:34:20+00:00 | mutation-changed | 0 | 188.79 | `.migration/harness/tools/afs-mutation` | `a4be13d41465b4a0` |  | gate=mutation score=0.971 threshold=0.8 killed=66 survived=2 files=1 base=b4373fca788d17c369e8b391a410a0bdde2d5765 |
| 2026-11-21T13:34:34+00:00 | build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:34:37+00:00 | build-check | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-21T13:34:39+00:00 | layers | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-21T13:34:41+00:00 | ui | 0 | 0.49 | `python .migration/harness/tools/check_ui.py` | `1d27b2ed2550b112` |  | gate=ui scope="templates changed since b4373fca788d17c369e8b391a410a0bdde2d5765" templates=5 findings=0 |
| 2026-11-21T13:35:33+00:00 | crap-coverage | 0 | 50.21 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `877c1b30ff70516e` |  |  |
| 2026-11-21T13:35:36+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T13:35:39+00:00 | crap | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `6bba55c28bb586fe` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-21T13:36:29+00:00 | regression | 0 | 48.13 | `pytest -q` | `00e511e3deacf2f5` |  |  |
| 2026-11-21T13:37:01+00:00 | return-validation | 1 | 4.84 | `python .migration/harness/tools/validate.py .migration` | `aea6ee1e593c79f2` | 195 file(s) checked, 3 error(s) |  |
| 2026-11-21T13:37:11+00:00 | return-validation | 1 | 4.84 | `python .migration/harness/tools/validate.py .migration` | `0b24613989b80412` | 195 file(s) checked, 2 error(s) |  |
| 2026-11-21T13:40:26+00:00 | mutation-changed | 0 | 188.27 | `python .migration/harness/tools/afs-mutation` | `2aebbed22524a227` |  | gate=mutation score=0.971 threshold=0.8 killed=66 survived=2 files=1 base=b4373fca788d17c369e8b391a410a0bdde2d5765 |
| 2026-11-21T13:40:37+00:00 | return-validation | 0 | 4.9 | `python .migration/harness/tools/validate.py .migration` | `7c75cd4a68d80691` |  |  |
