# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T21:39:28+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:42:38+00:00 | dialogs-red | 2 | 3.87 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2193dafcd502753b` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-19T21:43:41+00:00 | dialogs-targeted | 1 | 2.84 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `ed91df60d0647427` | assert response.status_code == 200 |  |
| 2026-11-19T21:43:52+00:00 | dialogs-targeted | 0 | 2.59 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `29cce0583b56b0ed` |  |  |
| 2026-11-19T21:44:26+00:00 | dialogs-targeted | 0 | 2.77 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `325400f4d722e218` |  |  |
| 2026-11-19T21:47:00+00:00 | dialogs-targeted | 0 | 2.86 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `9ff30fafd8346a4e` |  |  |
| 2026-11-19T21:47:57+00:00 | build-compileall | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:47:57+00:00 | build-django-check | 0 | 0.24 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T21:48:02+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T21:48:02+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T21:48:02+00:00 | idiom-layers | 0 | 0.09 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T21:48:02+00:00 | idiom-ui | 0 | 0.3 | `python .migration/harness/tools/check_ui.py` | `5c633968d13de30c` |  | gate=ui scope="templates changed since cce147dc5b1f06341760dbe4bbf1925210133037" templates=3 findings=0 |
| 2026-11-19T21:48:45+00:00 | behavior | 0 | 36.76 | `pytest -q` | `231b307c16ace022` |  |  |
| 2026-11-19T21:49:25+00:00 | crap-coverage | 0 | 32.93 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `92de76805bb9f081` |  |  |
| 2026-11-19T21:49:25+00:00 | crap-lizard | 0 | 0.09 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T21:49:25+00:00 | crap-score | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `c9ec3208e4f5c3e3` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-19T21:51:10+00:00 | dialogs-no-js-red | 1 | 1.88 | `pytest -q tests/booking/interfaces/test_dialogs.py -k non_htmx` | `8c8022284f95d14c` | assert page.status_code == 200 |  |
| 2026-11-19T21:51:16+00:00 | mutation-changed | 1 | 103.38 | `python .migration/harness/tools/afs-mutation` | `9b3761aa05bfa4eb` | afs-mutation: FAILED score=0.727 threshold=0.8 killed=48 survived=18 skipped=0 files=1 jobs=1 base=cce147dc5b1f06341760d | gate=mutation score=0.727 threshold=0.8 killed=48 survived=18 files=1 base=cce147dc5b1f06341760dbe4bbf1925210133037 |
| 2026-11-19T21:52:35+00:00 | dialogs-targeted | 0 | 3.98 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `6952f4ed683bae13` |  |  |
