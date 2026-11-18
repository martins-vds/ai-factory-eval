# Run journal: BK-05K

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-18T22:04:44+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T22:08:35+00:00 | red | 1 | 5.02 | `pytest -q tests/test_htmx_errors.py` | `24b0bae78b65fbf7` | assert response.status_code == 500 |  |
| 2026-11-18T22:08:55+00:00 | red-corrected | 1 | 4.16 | `pytest -q tests/test_htmx_errors.py` | `b5ca78e982bcdc5c` | assert response.status_code == 500 |  |
| 2026-11-18T22:09:36+00:00 | red-final | 1 | 4.08 | `pytest -q tests/test_htmx_errors.py` | `7c72b06e58b55ec6` | assert response.status_code == 500 |  |
| 2026-11-18T22:09:55+00:00 | focused-green | 0 | 4.0 | `pytest -q tests/test_htmx_errors.py` | `9e7581cfbdec7e91` |  |  |
| 2026-11-18T22:10:00+00:00 | ui-all | 0 | 0.32 | `python .migration/harness/tools/check_ui.py --all` | `0cb805740bfb2d16` |  | gate=ui scope="every template" templates=21 findings=0 |
| 2026-11-18T22:10:39+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T22:10:45+00:00 | build-check | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-18T22:10:48+00:00 | ruff-check | 1 | 0.03 | `ruff check` | `618ca838ec8319d2` | Found 1 error. |  |
| 2026-11-18T22:10:57+00:00 | ruff-check-rerun | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T22:11:00+00:00 | ruff-format | 0 | 0.03 | `ruff format --check` | `02bed28762c49640` |  |  |
| 2026-11-18T22:11:11+00:00 | layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `59bfd54275a9b5a4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-18T22:11:15+00:00 | ui-changed | 0 | 0.35 | `python .migration/harness/tools/check_ui.py` | `ce9e0484bc0f7c63` |  | gate=ui scope="templates changed since origin/main" templates=2 findings=0 |
| 2026-11-18T22:12:47+00:00 | behavior | 0 | 88.21 | `pytest -q` | `1ac285edb426d33a` |  |  |
| 2026-11-18T22:14:18+00:00 | crap-coverage | 0 | 85.36 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `ab11dcae27a46363` |  |  |
| 2026-11-18T22:14:23+00:00 | crap-lizard | 0 | 0.18 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-18T22:14:27+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `dbeb57242d6b2a6b` |  | gate=crap max=26.0 threshold=30 over=0 methods=213 |
| 2026-11-18T22:14:32+00:00 | mutation-changed | 0 | 0.09 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `36603172da4a0d74` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=origin/main |
| 2026-11-18T22:16:05+00:00 | regression | 0 | 76.14 | `pytest -q` | `c2aab12ea8c91682` |  |  |
| 2026-11-18T22:18:37+00:00 | focused-assertions | 0 | 4.0 | `pytest -q tests/test_htmx_errors.py` | `0f03d454dd7d0a3a` |  |  |
| 2026-11-18T22:18:41+00:00 | ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T22:18:45+00:00 | ruff-format-final | 0 | 0.01 | `ruff format --check` | `02bed28762c49640` |  |  |
| 2026-11-18T22:20:07+00:00 | regression-final | 0 | 75.53 | `pytest -q` | `b9b679cd673b15eb` |  |  |
| 2026-11-18T22:25:53+00:00 | focused-expired-cargo | 0 | 4.14 | `pytest -q tests/test_htmx_errors.py` | `7ded2b4efd0963a6` |  |  |
| 2026-11-18T22:25:58+00:00 | ruff-check-post-review | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-18T22:27:28+00:00 | regression-post-review | 0 | 85.3 | `pytest -q` | `eefdf9d8c6b07f3f` |  |  |
