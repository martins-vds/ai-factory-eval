# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T13:55:57+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:04:30+00:00 | tests-red | 2 | 4.19 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `f752dd7ff1ce6ae2` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-19T14:05:39+00:00 | tests-dialogs | 0 | 3.51 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `0778f18226c8c63a` |  |  |
| 2026-11-19T14:06:19+00:00 | tests-dialogs | 0 | 4.17 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `e9b9a43cb03fcd3d` |  |  |
| 2026-11-19T14:07:40+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:07:41+00:00 | build-django-check | 0 | 0.33 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-19T14:07:41+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-19T14:07:41+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `5b710ff7a343c343` |  |  |
| 2026-11-19T14:07:41+00:00 | idiom-layers | 0 | 0.13 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-19T14:07:41+00:00 | idiom-ui | 0 | 0.4 | `python .migration/harness/tools/check_ui.py` | `688c9036009c647c` |  | gate=ui scope="templates changed since ce7fef4539e78f730bcfb48037e18da46e6b6d7b" templates=2 findings=0 |
| 2026-11-19T14:08:36+00:00 | behavior | 0 | 49.22 | `pytest -q` | `d0fe23e6729d349f` |  |  |
| 2026-11-19T14:09:29+00:00 | crap-coverage | 0 | 47.42 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `93bb83250e8aa82a` |  |  |
| 2026-11-19T14:09:29+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T14:09:29+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `9c0a5fae73dec1c8` |  | gate=crap max=26.0 threshold=30 over=0 methods=206 |
| 2026-11-19T14:14:08+00:00 | tests-dialogs-final | 0 | 4.26 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `410cf0d46ea63b05` |  |  |
| 2026-11-19T14:14:08+00:00 | idiom-ui-final | 0 | 0.42 | `python .migration/harness/tools/check_ui.py` | `d3d977f04498d8c9` |  | gate=ui scope="templates changed since ce7fef4539e78f730bcfb48037e18da46e6b6d7b" templates=3 findings=0 |
