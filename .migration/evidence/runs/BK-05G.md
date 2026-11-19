# Run journal: BK-05G

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-07T23:07:55+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:14:06+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-19T18:17:36+00:00 | tdd-red-destination | 2 | 3.34 | `pytest -q tests/booking/interfaces/test_dialogs.py -k destination_dialog_excludes_origin_and_current_destination_without_mutating_locations` | `23ce79c7d0481ba1` | __________ ERROR collecting tests/booking/interfaces/test_dialogs.py ___________ |  |
| 2026-11-19T18:18:01+00:00 | tdd-green-destination | 0 | 2.29 | `pytest -q tests/booking/interfaces/test_dialogs.py -k destination_dialog_excludes_origin_and_current_destination_without_mutating_locations` | `48d1e350f94062d9` |  |  |
| 2026-11-19T18:18:24+00:00 | tdd-red-deadline | 1 | 2.27 | `pytest -q tests/booking/interfaces/test_dialogs.py -k invalid_deadline_shows_field_error_and_keeps_entered_value` | `aaa5664b552c814f` | assert response.status_code == 200 |  |
| 2026-11-19T18:18:43+00:00 | tdd-green-deadline | 0 | 2.23 | `pytest -q tests/booking/interfaces/test_dialogs.py -k invalid_deadline_shows_field_error_and_keeps_entered_value` | `925eefb519fd955b` |  |  |
| 2026-11-19T18:18:59+00:00 | tdd-deadline-update | 0 | 2.34 | `pytest -q tests/booking/interfaces/test_dialogs.py -k deadline_update_preserves_other_route_specification_fields_and_redirects` | `0b9fbe10699675d7` |  |  |
| 2026-11-19T18:19:16+00:00 | tdd-red-destination-update | 1 | 2.3 | `pytest -q tests/booking/interfaces/test_dialogs.py -k destination_update_preserves_other_route_specification_fields_and_redirects` | `3ff7efb0ad7c0070` | assert cargo_before is not None |  |
| 2026-11-19T18:19:30+00:00 | tdd-green-destination-update | 0 | 2.21 | `pytest -q tests/booking/interfaces/test_dialogs.py -k destination_update_preserves_other_route_specification_fields_and_redirects` | `ea177c190e166654` |  |  |
| 2026-11-19T18:19:49+00:00 | tdd-red-table-triggers | 1 | 2.19 | `pytest -q tests/booking/interfaces/test_dialogs.py -k not_routed_table_opens_destination_and_deadline_dialogs` | `1a3daa7009b85710` | assert 'href="/admin/cargo/DEF789/route/"' in content |  |
| 2026-11-19T18:20:11+00:00 | tdd-green-table-triggers | 0 | 2.13 | `pytest -q tests/booking/interfaces/test_dialogs.py -k not_routed_table_opens_destination_and_deadline_dialogs` | `2b678cb62dc9e212` |  |  |
| 2026-11-19T18:20:37+00:00 | dialogs-targeted | 1 | 4.57 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `9dda32ca554f3043` | assert response.status_code == 200 |  |
| 2026-11-19T18:20:54+00:00 | dialogs-targeted | 0 | 4.35 | `pytest -q tests/booking/interfaces/test_dialogs.py` | `16cd6133529bb348` |  |  |
| 2026-11-19T18:21:29+00:00 | focused-regression | 0 | 5.49 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `117fea6583e457b3` |  |  |
| 2026-11-19T18:21:50+00:00 | focused-regression | 0 | 5.52 | `pytest -q tests/booking/interfaces/test_dialogs.py tests/booking/interfaces/test_dashboard.py` | `117fea6583e457b3` |  |  |
