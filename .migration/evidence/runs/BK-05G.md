# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-20T00:35:07+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:39:12+00:00 | dialogs-red | 2 | 2.28 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `2bfec778546d61b5` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-20T00:41:34+00:00 | dialogs-targeted | 0 | 3.76 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `99354c619c9ab448` |  |  |
| 2026-11-20T00:42:29+00:00 | dialogs-targeted | 0 | 4.98 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8947f82fe72ecb2f` |  |  |
| 2026-11-20T00:42:43+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:42:43+00:00 | build-django-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T00:42:43+00:00 | idiom-ruff-check | 1 | 0.02 | `ruff check` | `759629dc8cbe0f32` | 82 \|     assert 'Hong Kong' in content |  |
| 2026-11-20T00:42:55+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:42:56+00:00 | build-django-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T00:42:56+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:42:56+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `e5c85f57df073d44` |  |  |
| 2026-11-20T00:43:06+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:43:07+00:00 | build-django-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T00:43:07+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T00:43:07+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-20T00:43:07+00:00 | idiom-layers | 0 | 0.11 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-20T00:43:07+00:00 | idiom-ui | 0 | 0.4 | `python .migration/harness/tools/check_ui.py` | `3b5a596487ce015f` |  | gate=ui scope="templates changed since b3b29def45ae6c8608e0427fddd7417d891deb42" templates=2 findings=0 |
| 2026-11-20T00:45:45+00:00 | behavior | 0 | 50.05 | `pytest -q` | `58f6325ac7d73adf` |  |  |
| 2026-11-20T00:46:43+00:00 | crap-coverage | 0 | 48.37 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `b4f8020f0e75335f` |  |  |
| 2026-11-20T00:46:43+00:00 | crap-lizard | 0 | 0.11 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T00:46:43+00:00 | crap | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0cea1cdfeb73461b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-20T00:48:52+00:00 | mutation_changed | 1 | 124.25 | `python .migration/harness/tools/afs-mutation` | `7135284210e21ad2` | afs-mutation: FAILED score=0.759 threshold=0.8 killed=41 survived=13 skipped=0 files=1 jobs=1 base=b3b29def45ae6c8608e04 | gate=mutation score=0.759 threshold=0.8 killed=41 survived=13 files=1 base=b3b29def45ae6c8608e0427fddd7417d891deb42 |
| 2026-11-20T00:49:52+00:00 | dialogs-targeted | 1 | 5.79 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `86aad9cd3c1e0531` | assert response.status_code == 404 |  |
| 2026-11-20T00:50:11+00:00 | dialogs-targeted | 0 | 5.6 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `d02ef780ea067584` |  |  |
| 2026-11-20T00:52:27+00:00 | mutation_changed | 0 | 128.41 | `python .migration/harness/tools/afs-mutation` | `e9e30c0e8a27f8b0` |  | gate=mutation score=0.849 threshold=0.8 killed=45 survived=8 files=1 base=b3b29def45ae6c8608e0427fddd7417d891deb42 |
| 2026-11-20T00:55:22+00:00 | dialogs-targeted | 0 | 5.77 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `af7d318033095906` |  |  |
| 2026-11-20T00:57:31+00:00 | mutation_changed | 0 | 125.75 | `python .migration/harness/tools/afs-mutation` | `20f436ec88326af7` |  | gate=mutation score=0.887 threshold=0.8 killed=47 survived=6 files=1 base=b3b29def45ae6c8608e0427fddd7417d891deb42 |
| 2026-11-20T01:01:22+00:00 | build-compile | 0 | 0.03 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T01:01:22+00:00 | build-django-check | 0 | 0.29 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-20T01:01:22+00:00 | idiom-ruff-check | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-20T01:01:22+00:00 | idiom-ruff-format | 0 | 0.01 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-20T01:01:22+00:00 | idiom-layers | 0 | 0.11 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-20T01:01:23+00:00 | idiom-ui | 0 | 0.41 | `python .migration/harness/tools/check_ui.py` | `9ed0e9c12cf763ee` |  | gate=ui scope="templates changed since b3b29def45ae6c8608e0427fddd7417d891deb42" templates=3 findings=0 |
| 2026-11-20T01:02:16+00:00 | behavior | 0 | 52.95 | `pytest -q` | `d716b25ba3ca5a77` |  |  |
| 2026-11-20T01:03:19+00:00 | crap-coverage | 0 | 63.07 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `8fdc36cfd3b67d9e` |  |  |
| 2026-11-20T01:03:19+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-20T01:03:19+00:00 | crap | 0 | 0.03 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `0cea1cdfeb73461b` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-20T01:04:09+00:00 | regression | 0 | 50.09 | `pytest -q` | `8e76cdacdffe5431` |  |  |
