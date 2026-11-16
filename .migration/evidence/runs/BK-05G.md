# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:35:36+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-16T20:38:51+00:00 | red-destination-dialog | 2 | 0.8 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `b10a6f0b78f6db33` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-16T20:39:25+00:00 | green-destination-initial | 1 | 1.42 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `147b628fdd5fa191` | assert cargo is not None |  |
| 2026-11-16T20:39:39+00:00 | green-destination-initial | 0 | 1.27 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a558b8376cd28466` |  |  |
| 2026-11-16T20:40:00+00:00 | destination-options | 1 | 1.57 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `c3b1d5a5ecd1fb96` | E       django.template.exceptions.TemplateDoesNotExist: booking/dialogs/deadline.html |  |
| 2026-11-16T20:40:10+00:00 | destination-options | 1 | 1.6 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `25af8d90605f8fe7` | assert locations == original_locations |  |
| 2026-11-16T20:40:20+00:00 | destination-options | 0 | 1.63 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `00b28118fe496cca` |  |  |
| 2026-11-16T20:40:34+00:00 | destination-update | 0 | 1.86 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `a971a7c2ec0752fd` |  |  |
| 2026-11-16T20:40:46+00:00 | red-deadline-invalid | 1 | 1.37 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_invalid_deadline_shows_a_field_error_without_changing_cargo` | `b40c02a09158f403` | assert cargo is not None |  |
| 2026-11-16T20:40:59+00:00 | green-deadline-invalid | 0 | 2.11 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `58a0ecfcf570da4b` |  |  |
| 2026-11-16T20:41:11+00:00 | deadline-update | 0 | 2.42 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `8f337870cb203dee` |  |  |
| 2026-11-16T20:41:23+00:00 | red-dashboard-launch | 1 | 1.37 | `pytest -q tests/booking/interfaces/test_dialogs.py::test_not_routed_table_opens_destination_and_deadline_dialogs` | `ebd6065123079d57` | assert cargo is not None |  |
| 2026-11-16T20:41:39+00:00 | green-dashboard-launch | 0 | 3.19 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `38315f851ae7c42c` |  |  |
| 2026-11-16T20:42:18+00:00 | focused-dialogs-dashboard | 0 | 3.32 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `2e6245b75f87acbf` |  |  |
| 2026-11-16T20:43:08+00:00 | focused-dialogs-dashboard | 0 | 3.7 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `dd5a4f11f76a4b9e` |  |  |
| 2026-11-16T20:43:49+00:00 | build | 0 | 0.25 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-16T20:43:52+00:00 | idiom | 1 | 0.03 | `bash -c 'ruff check && ruff format --check'` | `bb4d64321f1c5da6` | 128 \|     assert updated_cargo is not None |  |
| 2026-11-16T20:44:07+00:00 | idiom | 0 | 0.02 | `bash -c 'ruff check && ruff format --check'` | `6a496cdbbfea65a9` |  |  |
| 2026-11-16T20:44:50+00:00 | crap | 0 | 35.05 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `22f7054b396f0f11` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-16T20:46:40+00:00 | mutation-changed | 1 | 104.65 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `62ae0ef7b35d0cf2` | afs-mutation: FAILED score=0.662 threshold=0.8 killed=45 survived=23 skipped=0 files=1 jobs=1 base=origin/main | gate=mutation score=0.662 threshold=0.8 killed=45 survived=23 files=1 base=origin/main |
| 2026-11-16T20:48:28+00:00 | focused-dialogs-dashboard | 1 | 4.11 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `8438a8d3623cbe3a` | assert destination_not_found.status_code == 404 |  |
| 2026-11-16T20:48:47+00:00 | focused-dialogs-dashboard | 0 | 4.1 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `55145c4f89c01d5a` |  |  |
| 2026-11-16T20:50:25+00:00 | mutation-changed | 0 | 93.67 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `efaf42274d2a5ef7` |  | gate=mutation score=0.925 threshold=0.8 killed=62 survived=5 files=1 base=origin/main |
| 2026-11-16T20:50:35+00:00 | idiom | 1 | 0.02 | `bash -c 'ruff check && ruff format --check'` | `4e13714feee2d2ff` | 155 \|     assert ( |  |
| 2026-11-16T20:50:57+00:00 | idiom | 0 | 0.02 | `bash -c 'ruff check && ruff format --check'` | `6a496cdbbfea65a9` |  |  |
| 2026-11-16T20:51:04+00:00 | focused-dialogs-dashboard | 0 | 3.94 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `62210fe5ce8477a3` |  |  |
| 2026-11-16T20:52:35+00:00 | mutation-changed | 0 | 86.14 | `python .migration/harness/tools/afs-mutation --changed-since origin/main` | `5c4d9813c7e9787c` |  | gate=mutation score=0.970 threshold=0.8 killed=64 survived=2 files=1 base=origin/main |
| 2026-11-16T20:54:41+00:00 | build | 0 | 0.24 | `bash -c 'python -m compileall -q src && python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-16T20:54:45+00:00 | idiom | 0 | 0.02 | `bash -c 'ruff check && ruff format --check'` | `6a496cdbbfea65a9` |  |  |
| 2026-11-16T20:55:23+00:00 | crap | 0 | 33.79 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov && lizard --csv src > .migration/runs/lizard.csv && python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `914d61be2a69e615` |  | gate=crap max=26.0 threshold=30 over=0 methods=205 |
| 2026-11-16T20:56:00+00:00 | regression | 0 | 32.1 | `pytest -q` | `1b49a8b7ecbb5222` |  |  |
| 2026-11-16T20:56:22+00:00 | behavior | 0 | 3.94 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `62210fe5ce8477a3` |  |  |
