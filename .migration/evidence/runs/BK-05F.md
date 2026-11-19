# Run journal: BK-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-19T18:14:00+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:17:32+00:00 | tests-red | 2 | 6.71 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `e4c9bca63593996c` | ______ ERROR collecting tests/booking/interfaces/test_route_selection.py _______ |  |
| 2026-11-19T18:18:19+00:00 | tests-targeted | 0 | 3.51 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `3eae56deae2700cc` |  |  |
| 2026-11-19T18:18:46+00:00 | ui-checks | 0 | 0.4 | `python .migration/harness/tools/check_ui.py` | `ffb4265bfa237c5d` |  | gate=ui scope="templates changed since 5ec4a4b699c3194294e74243c50dea12b0e76163" templates=4 findings=0 |
| 2026-11-19T18:20:21+00:00 | tests-targeted | 0 | 3.91 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `6e6f3388206fe0be` |  |  |
| 2026-11-19T18:21:28+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:21:33+00:00 | build-django-check | 0 | 0.31 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T18:22:24+00:00 | behavior | 0 | 48.04 | `pytest -q` | `dbcd9895af0e2d9f` |  |  |
| 2026-11-19T18:22:34+00:00 | idiom-ruff-check | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T18:22:39+00:00 | idiom-ruff-format | 1 | 0.02 | `ruff format --check` | `97f9e92869bb003f` |  |  |
| 2026-11-19T18:22:52+00:00 | tests-targeted | 0 | 3.65 | `pytest -q tests/booking/interfaces/test_route_selection.py` | `3b1127cade8fe5e5` |  |  |
