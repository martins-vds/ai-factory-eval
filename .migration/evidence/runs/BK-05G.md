# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:27:29+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:31:09+00:00 | dialogs-red | 2 | 1.36 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8fc2cc9247cc46e4` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-22T17:32:06+00:00 | dialogs-targeted | 1 | 4.73 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `d312d746bed81c3f` | assert first_response.status_code == 200 |  |
| 2026-11-22T17:32:34+00:00 | dialogs-targeted | 1 | 4.75 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `04d9fbaee3bdf636` | assert cargo is not None |  |
| 2026-11-22T17:32:50+00:00 | dialogs-targeted | 0 | 4.67 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `3043b238ba5b8844` |  |  |
| 2026-11-22T17:33:26+00:00 | behavior-targeted | 0 | 5.88 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py tests/booking/application/test_specification.py` | `edc89db40b004151` |  |  |
| 2026-11-22T17:34:09+00:00 | lint | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T17:34:11+00:00 | format-check | 0 | 0.03 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-22T17:34:13+00:00 | layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-22T17:34:16+00:00 | ui | 0 | 0.68 | `python .migration/harness/tools/check_ui.py` | `84cefff2e924ad56` |  | gate=ui scope="templates changed since b14caa72d9717a35bb5fb17495b487c6545a0334" templates=4 findings=0 |
| 2026-11-22T17:34:21+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T17:34:23+00:00 | build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T17:36:36+00:00 | regression | 0 | 64.96 | `pytest -q` | `6e68d21a31aa1eff` |  |  |
| 2026-11-22T17:39:38+00:00 | mutation-changed | 1 | 178.76 | `python .migration/harness/tools/afs-mutation` | `84f0ab88f589ae89` | afs-mutation: FAILED score=0.684 threshold=0.8 killed=52 survived=24 skipped=0 files=1 jobs=1 base=b14caa72d9717a35bb5fb | gate=mutation score=0.684 threshold=0.8 killed=52 survived=24 files=1 base=b14caa72d9717a35bb5fb17495b487c6545a0334 |
| 2026-11-22T17:40:45+00:00 | dialogs-targeted | 0 | 6.07 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `de4f93ea8f54b468` |  |  |
| 2026-11-22T17:40:49+00:00 | lint | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T17:40:52+00:00 | format-check | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-22T17:43:25+00:00 | mutation-changed | 0 | 148.23 | `python .migration/harness/tools/afs-mutation` | `9f72051b537227a6` |  | gate=mutation score=1.000 threshold=0.8 killed=66 survived=0 files=1 base=b14caa72d9717a35bb5fb17495b487c6545a0334 |
