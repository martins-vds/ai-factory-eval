# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:41:18+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:44:14+00:00 | behavior-dashboard | 0 | 4.73 | `pytest -q tests/booking/interfaces/test_dashboard.py` | `7e12aaa8f9a073d9` |  |  |
| 2026-11-17T21:44:59+00:00 | build-compile | 0 | 0.06 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:44:59+00:00 | build-check | 0 | 0.3 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-17T21:45:02+00:00 | idiom-lint | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-17T21:45:02+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `35ff24d8a92c0ac9` |  |  |
| 2026-11-17T21:45:49+00:00 | regression | 0 | 44.5 | `pytest -q` | `309491cb7d2705db` |  |  |
| 2026-11-17T21:46:34+00:00 | crap-coverage | 0 | 41.88 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `1352ee8c037535cf` |  |  |
| 2026-11-17T21:46:34+00:00 | crap-lizard | 0 | 0.12 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-17T21:46:34+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `38474ed587bda142` |  | gate=crap max=26.0 threshold=30 over=0 methods=200 |
