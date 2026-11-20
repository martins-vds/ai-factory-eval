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
