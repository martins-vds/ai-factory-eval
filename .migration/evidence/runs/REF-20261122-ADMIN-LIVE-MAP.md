# Run journal: REF-20261122-ADMIN-LIVE-MAP

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T22:46:14+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T22:47:11+00:00 | behavior-targeted | 0 | 3.57 | `pytest -q tests/cargo/interfaces/test_admin_live_map_data.py` | `ebc0f53354694c7d` |  |  |
| 2026-11-22T22:47:31+00:00 | build-compile | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T22:47:34+00:00 | build-django-check | 0 | 0.37 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-22T22:47:36+00:00 | spec | 0 | 0.06 | `python .migration/harness/tools/afs-spec run` | `1b0b939f3e1e502f` |  | gate=spec cases=0 failed=0 pending=0 |
| 2026-11-22T22:47:38+00:00 | idiom-ruff-check | 1 | 0.03 | `ruff check` | `80d46ad736c8dcbb` |  |  |
| 2026-11-22T22:47:47+00:00 | idiom-ruff-check-retry | 1 | 0.01 | `ruff check` | `8bd8b7309d96680f` |  |  |
| 2026-11-22T22:48:12+00:00 | idiom-ruff-check-final | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-22T22:48:14+00:00 | idiom-ruff-format | 0 | 0.03 | `ruff format --check` | `b221fa32ed80fb2e` |  |  |
| 2026-11-22T22:48:16+00:00 | idiom-layers | 0 | 0.14 | `python .migration/harness/tools/check_layers.py` | `59bfd54275a9b5a4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-22T22:48:19+00:00 | idiom-ui | 0 | 0.57 | `python .migration/harness/tools/check_ui.py` | `a40e133d2d464694` |  | gate=ui scope="templates changed since 0eb33070a765c30ce7c99fe4c30112d1d8bba842" templates=0 findings=0 |
| 2026-11-22T22:49:42+00:00 | crap-coverage | 0 | 79.92 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `928668c71b40d15e` |  |  |
| 2026-11-22T22:49:45+00:00 | crap-lizard | 0 | 0.13 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T22:49:48+00:00 | crap-threshold | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `dbeb57242d6b2a6b` |  | gate=crap max=26.0 threshold=30 over=0 methods=213 |
| 2026-11-22T22:51:07+00:00 | mutation-changed | 0 | 76.68 | `python .migration/harness/tools/afs-mutation` | `584f9a02f3491a8b` |  | gate=mutation score=0.973 threshold=0.8 killed=36 survived=1 files=2 base=0eb33070a765c30ce7c99fe4c30112d1d8bba842 |
| 2026-11-22T22:51:16+00:00 | behavior | 0 | 3.01 | `pytest -q tests/cargo/interfaces/test_admin_live_map_data.py` | `e0fd74d83521f884` |  |  |
| 2026-11-22T22:52:25+00:00 | regression | 0 | 66.49 | `pytest -q` | `cf275ea896b4547b` |  |  |
