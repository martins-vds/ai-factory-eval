# Run journal: DM-05F

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-23T01:34:54+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:37:07+00:00 | invariants-targeted | 0 | 2.56 | `pytest -q tests/data_migration/test_invariants.py` | `99b46a9054cdd02b` |  |  |
| 2026-11-23T01:37:26+00:00 | build-compile | 0 | 0.07 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:37:27+00:00 | build-django-check | 0 | 0.38 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T01:37:30+00:00 | idiom-ruff | 0 | 0.02 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T01:37:30+00:00 | idiom-format | 1 | 0.02 | `ruff format --check` | `aeacfc91fbcbb862` | 202 \|     assert cargo.delivery.misdirected == derived.misdirected |  |
| 2026-11-23T01:37:30+00:00 | idiom-layers | 0 | 0.16 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-23T01:37:31+00:00 | idiom-ui | 0 | 0.71 | `python .migration/harness/tools/check_ui.py` | `0f20836564fe9488` |  | gate=ui scope="templates changed since 1a60fd5e13f6ee4890a06c7a734715bbce2c804d" templates=0 findings=0 |
| 2026-11-23T01:37:36+00:00 | idiom-format-fix | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T01:37:38+00:00 | invariants-after-format | 0 | 2.15 | `pytest -q tests/data_migration/test_invariants.py` | `1b10789e86b1daf8` |  |  |
| 2026-11-23T01:38:44+00:00 | behavior-suite | 0 | 52.16 | `pytest -q` | `04b500473f245003` |  |  |
| 2026-11-23T01:39:36+00:00 | crap-coverage | 0 | 47.84 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `022cef9e2fa4525a` |  |  |
| 2026-11-23T01:39:39+00:00 | crap-lizard | 0 | 0.15 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:39:41+00:00 | crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-23T01:39:43+00:00 | mutation-changed | 0 | 0.09 | `python .migration/harness/tools/afs-mutation` | `23ddba20874117fe` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=1a60fd5e13f6ee4890a06c7a734715bbce2c804d |
| 2026-11-23T01:40:12+00:00 | final-build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:40:12+00:00 | final-build-check | 0 | 0.36 | `python manage.py check` | `1e3e63f221bde888` |  |  |
| 2026-11-23T01:40:12+00:00 | final-ruff | 0 | 0.01 | `ruff check` | `82b3e6a6c090a576` |  |  |
| 2026-11-23T01:40:12+00:00 | final-format | 0 | 0.01 | `ruff format --check` | `9eb349efea514fbe` |  |  |
| 2026-11-23T01:40:13+00:00 | final-layers | 0 | 0.17 | `python .migration/harness/tools/check_layers.py` | `6d772d1f98375ff4` | src/cargotracker/booking/application/routing.py:1: known, not failing: use cases don't depend on web adapters or persist | gate=layering contracts=3 violations=0 known=3 |
| 2026-11-23T01:40:13+00:00 | final-ui | 0 | 0.71 | `python .migration/harness/tools/check_ui.py` | `0f20836564fe9488` |  | gate=ui scope="templates changed since 1a60fd5e13f6ee4890a06c7a734715bbce2c804d" templates=0 findings=0 |
| 2026-11-23T01:41:15+00:00 | final-regression | 0 | 58.48 | `pytest -q` | `a5f17686c08738a8` |  |  |
| 2026-11-23T01:42:08+00:00 | final-crap-coverage | 0 | 50.9 | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov` | `2650e86b84b77025` |  |  |
| 2026-11-23T01:42:11+00:00 | final-crap-lizard | 0 | 0.16 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:42:11+00:00 | final-crap-score | 0 | 0.04 | `python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | `cd986f492a47b1ae` |  | gate=crap max=26.0 threshold=30 over=0 methods=177 |
| 2026-11-23T01:42:11+00:00 | final-mutation-changed | 0 | 0.09 | `python .migration/harness/tools/afs-mutation` | `23ddba20874117fe` |  | gate=mutation score=n/a reason=no-mutable-code-changed base=1a60fd5e13f6ee4890a06c7a734715bbce2c804d |
| 2026-11-23T01:44:46+00:00 | finish-build-compile | 0 | 0.04 | `python -m compileall -q src` | `e3b0c44298fc1c14` |  |  |
| 2026-11-23T01:44:47+00:00 | finish-build-check | 0 | 0.39 | `python manage.py check` | `1e3e63f221bde888` |  |  |
