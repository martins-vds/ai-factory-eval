# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-15T15:03:21+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T15:06:29+00:00 | invariants-tests | 1 | 6.56 | `pytest -q tests/data_migration/test_invariants.py` | `7fd98e3b0a8ed682` | >           assert replace(derived, last_event_id=history.most_recent_event_id) == cargo.delivery |  |
| 2026-11-15T15:06:53+00:00 | invariants-tests | 0 | 2.28 | `pytest -q tests/data_migration/test_invariants.py` | `f007a127784409c8` |  |  |
| 2026-11-15T15:07:34+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T15:07:39+00:00 | build-check | 0 | 0.42 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-15T15:07:43+00:00 | idiom-ruff | 1 | 0.02 | `ruff check` | `0857e67097c9afbc` | 172 \|         assert all( |  |
| 2026-11-15T15:07:55+00:00 | idiom-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T15:07:59+00:00 | idiom-format | 0 | 0.02 | `ruff format --check` | `1e2a3e2494e870c6` |  |  |
| 2026-11-15T15:09:03+00:00 | behavior | 0 | 59.67 | `pytest -q` | `0ebd7dcd4615a78d` |  |  |
| 2026-11-15T15:10:02+00:00 | crap-coverage | 0 | 54.35 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `446b30a2458b7023` |  |  |
| 2026-11-15T15:10:07+00:00 | crap-threshold | 0 | 0.2 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-15T15:36:31+00:00 | invariants-tests-final | 0 | 2.27 | `pytest -q tests/data_migration/test_invariants.py` | `f007a127784409c8` |  |  |
| 2026-11-15T15:36:35+00:00 | snapshot-check | 0 | 0.06 | `python .migration/harness/tools/data_reconcile.py snapshot .migration/data/snapshot` | `bee2f0acd5234102` |  | gate=data-snapshot tables=7 problems=0 |
| 2026-11-15T15:36:39+00:00 | idiom-ruff-final | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-15T15:36:43+00:00 | idiom-format-final | 0 | 0.01 | `ruff format --check` | `1e2a3e2494e870c6` |  |  |
| 2026-11-15T15:37:38+00:00 | behavior-final | 0 | 51.16 | `pytest -q` | `1c10a7943687653a` |  |  |
| 2026-11-15T15:38:37+00:00 | crap-coverage-final | 0 | 51.41 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `c8c8aeb39c3aed3f` |  |  |
| 2026-11-15T15:38:41+00:00 | crap-threshold-final | 0 | 0.2 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-15T15:39:45+00:00 | regression-final | 0 | 61.34 | `pytest -q` | `53dc6b64ab25d572` |  |  |
| 2026-11-15T15:39:51+00:00 | build-compile-final | 0 | 0.05 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-15T15:39:55+00:00 | build-check-final | 0 | 0.41 | `python manage.py check` | `1e3e63f221bde888` |  |  |
