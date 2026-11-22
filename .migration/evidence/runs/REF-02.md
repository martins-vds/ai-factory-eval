# Run journal: REF-02

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-22T14:31:26+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-22T14:32:27+00:00 | targeted-endpoints | 0 | 13.72 | `pytest -q tests/fees/test_endpoints.py` | `6afce70c151dec4b` |  |  |
| 2026-11-22T14:32:48+00:00 | build | 0 | 0.47 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-22T14:33:06+00:00 | behavior | 0 | 15.64 | `pytest -q` | `b41a68c1b7fac47d` |  |  |
| 2026-11-22T14:33:10+00:00 | idiom | 0 | 0.75 | `bash -c 'ruff check src config manage.py tests && ruff format --check src config manage.py tests && python .migration/harness/tools/check_layers.py && python .migration/harness/tools/check_ui.py'` | `1cdd1a8c106b7d83` |  | gate=ui scope="templates changed since 0d8da25f33558c65a9c5a37496804eee56e28fff" templates=0 findings=0 |
| 2026-11-22T14:33:29+00:00 | crap | 0 | 17.06 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `8d0761877d7529df` |  | gate=crap max=7.0 threshold=30 over=0 methods=46 |
| 2026-11-22T14:38:30+00:00 | mutation-changed | 0 | 298.91 | `python .migration/harness/tools/afs-mutation` | `c649b89a63dad5e3` |  | gate=mutation score=1.000 threshold=0.8 killed=61 survived=0 files=2 base=0d8da25f33558c65a9c5a37496804eee56e28fff |
| 2026-11-22T14:38:49+00:00 | regression | 0 | 15.53 | `pytest -q` | `14197f564ae6a813` |  |  |
