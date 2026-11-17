# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:12:22+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:15:02+00:00 | dashboard-tests | 0 | 5.15 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `16ea4f870f6be017` |  |  |
| 2026-11-17T21:15:42+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:15:43+00:00 | build-check | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-17T21:15:43+00:00 | idiom-ruff | 0 | 0.03 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:15:43+00:00 | idiom-format | 0 | 0.03 | `ruff format --check` | `35ff24d8a92c0ac9` |  |  |
| 2026-11-17T21:15:54+00:00 | behavior | 0 | 2.92 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `51dda580d2918aa0` |  |  |
| 2026-11-17T21:16:55+00:00 | regression | 0 | 61.04 | `pytest -q` | `af2a1e8dd6865dd1` |  |  |
| 2026-11-17T21:17:55+00:00 | crap-coverage | 0 | 59.79 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `f37e05b2a11f9a34` |  |  |
| 2026-11-17T21:17:55+00:00 | crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:17:55+00:00 | crap-threshold | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `38474ed587bda142` |  | gate=crap max=26.0 threshold=30 over=0 methods=200 |
