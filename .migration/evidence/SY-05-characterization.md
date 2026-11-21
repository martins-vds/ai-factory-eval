# SY-05 characterization evidence

Source pinned to commit `563c316ed51462b08fd6e58f3781a3c8b2890453`; characterization tier A used the existing `.migration/characterization/source/characterize.py` harness against the running legacy application.

## Legacy tests

No legacy test directory or `*Test.java` / `*IT.java` files exist in `legacy/`. The characterization suite itself is the only executable legacy coverage added for this run.

## Observed behavior

The suite exercised all seven graph endpoints, six additional normal/error edge cases, and two browser pages.

| Ledger capability | Observation | Predicted versus observed |
|---|---|---|
| `about.page` | `GET /about` returned 200 HTML with the 14-day, hours, and contact text. | Match. |
| `app.startup` | `./run.sh` built and started the application on port 8080; shutdown hooks close JPA and HTTP state. | Match. |
| `loan.list`, `csv.export-contract` | `GET /loans` returned 200 newline-terminated semicolon records ordered by ID. | Match. |
| `loan.get` | `GET /loans/L1` returned 200; `/loans/UNKNOWN` returned 404 `no such loan`. | Match. |
| `loan.lend` | Missing form fields returned 400; valid fields returned 201 and a 14-day due date. Empty `member` and `isbn` values returned 201 with empty fields. | Empty-string behavior differs from the ledger requirement that both fields be required. |
| `loan.return` | `POST /loans/L1/return` returned 200 and today's return date; unknown ID returned 404. | Match. |
| `loan.entity` | Lent and due dates showed the entity's 14-day rule in actual loan lines. | Match. |
| `loan.repository` | List, find, lend, and mark-returned operations succeeded through HTTP and committed updates in the running in-memory database. | Match. |
| `loan.persistence` | Startup used in-memory H2 with drop/create schema and seed loading. | Match. |
| `loan.seed-data` | Startup served fixed seed rows L1, L2, and L3. | Match. |
| `fee.view` | `GET /fees/L3` returned the due date, late days, and $4.75; unknown loan returned 404 HTML. | Match. |
| `payment.charge`, `payment.gateway-config` | Known L3 produced 502 `payment gateway unavailable` with the default external gateway unavailable; unknown loan returned 404. | Match for configured default/HTTP status behavior. |
| `monthly-report.spec` | No runnable report code or service exists; only `legacy/docs/reports-spec.md:1-8` remains. | Spec-derived only: 0 runtime matches and 0 runtime differences can be claimed. |

## New quirk

`loan.lend` accepts empty form values because validation checks only `null`. Draft: `.migration/quirks/empty-loan-fields.md`.
