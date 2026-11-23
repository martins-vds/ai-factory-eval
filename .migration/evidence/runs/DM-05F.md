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
