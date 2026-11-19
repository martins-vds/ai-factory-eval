# BK-05G UI end-to-end evidence

- Run: 2026-11-19, manual Playwright browser interaction against the local Django server.
- Setup: isolated `cargotracker_bk05g_e2e` database migrated and seeded with sample data; generated Tailwind CSS was served successfully. The database, temporary settings, and temporary URL configuration were removed after the run.
- URL configuration: `tests.booking.interfaces.test_dialogs` was used for this slice's endpoints. Central application URL registration remains BK-05H scope, as recorded in `.migration/plan/booking.md`.

## Flows

1. Opened `/admin/dashboard/`; the `DEF789` not-routed row showed destination and deadline buttons while its route link remained `/admin/cargo/DEF789/route/`.
2. Opened the destination dialog. Its initial value and choices were rendered; origin and current destination were excluded. Selected Helsinki and submitted. The browser received the successful update response, followed the htmx redirect, showed Helsinki in the refreshed row, and closed the dialog.
3. Opened the deadline dialog, confirmed its current value, changed it to `2027-01-20`, and submitted. The browser followed the htmx redirect, showed `01/20/2027` in the refreshed row, and closed the dialog.

The browser network log showed dashboard/dialog GETs returning 200, update POSTs returning 204, refreshed dashboard GETs returning 200, and the Tailwind stylesheet returning 200/304. No browser console errors were reported. The native required date input prevented an empty value from being submitted; malformed and missing values are separately covered by `tests/booking/interfaces/test_dialogs.py::test_invalid_deadline_shows_field_error_and_keeps_dialog_open`.
