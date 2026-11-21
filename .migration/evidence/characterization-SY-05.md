# SY-05 — Legacy characterization

## Source and test inventory

- Source: `martins-vds/ai-factory-synthetic-target`, SHA `563c316ed51462b08fd6e58f3781a3c8b2890453`, `legacy/`.
- The source built and ran on OpenJDK 17.0.21 with Maven 3.10.1. The characterization runner launched it twice on port 8080.
- No legacy test sources were found under `.source/legacy`; the inventory command is recorded in `.migration/evidence/runs/SY-05.md`.
- The monthly-report capability is different: its source explicitly says the implementation and runtime are unavailable. It is characterized at tier C from `legacy/docs/reports-spec.md`.

## Suite and coverage

The existing harness was extended, not replaced. Its tier-A run checks seven graph endpoints, 13 additional HTTP scenarios, two browser pages, and the post-restart loan list: **23 checks, all passing**. The first list and post-restart list matched; after mutations, restarting restored the three seeded loans.

The source predictions matched every runnable observation (23 matches, 0 differences). The suite run and its raw-log hashes are in `.migration/evidence/runs/SY-05.md`. JaCoCo observed 93/98 lines, 482/513 instructions, and 16/20 branches. The refreshed source risk map is `.migration/risk-map/SY-05.md` (maximum CRAP 4.0; no method exceeds 30).

## Capability observations

| Capability | Tier | Predicted from source | Observed |
|---|---:|---|---|
| `about.page` | A | `/about` returns the static HTML page. | HTTP 200 HTML; Chromium displays “About the Lending Library”. |
| `application.startup` | A | Initialize persistence and register the REST resources before listening. | Both launches became ready; HTTP and browser probes succeeded. Restart reset the database as described below. |
| `data.loan-storage` | A | Use in-memory H2 with a recreated schema at startup. | After creating and returning loans, a new process served only the original seeds. |
| `data.seed-records` | A | Load seed loans L1–L3. | Initial `GET /loans` returned L1, L2, L3 in that order. |
| `fees.calculate` | A | Waive up to two late days, then charge 25 cents/day, capped at $10. | L1: $10.00 cap; L2: 0 days/$0.00; L3: 19 days/$4.75. |
| `fees.find-loan` | A | Return the fee page for an existing loan and 404 for a missing one. | L3 returned HTTP 200; missing ID returned HTTP 404, `<p>No such loan.</p>`. |
| `fees.render` | A | Render a late-fee page as HTML. | `/fees/L3` returned HTML with heading “Late fee for L3”; Chromium read the same heading. |
| `integration.payment-gateway` | A | A known loan invokes the configured gateway; the default URL is unavailable. | `POST /payments/L3` returned HTTP 502, `payment gateway unavailable`; no successful gateway response was available. |
| `loan.entity` | A | A loan has identity, member, ISBN, lent/return dates, and a 14-day due date. | Seed records and new L4–L6 showed those fields; new loans were due 14 days after creation. |
| `loan.return-date` | A | A return writes today's date, including on an already-returned loan. | Returning L1 wrote 2026-11-21; repeating the route for L2 replaced its seed return date with 2026-11-21. |
| `loan.return` | A | Return an existing loan; report a missing ID as 404. | L1 and already-returned L2 returned HTTP 200; a missing ID returned HTTP 404, `no such loan`. |
| `loans.create-input` | A | Missing form parameters return 400; the null check does not reject blank strings. | Missing member or ISBN returned HTTP 400; both blank fields returned HTTP 201. |
| `loans.create-persist` | A | Persist a new loan with ID based on row count. | L4–L6 appeared in the subsequent list; concurrent ID collision behavior was not deterministically exercised. |
| `loans.create-response` | A | Successful creation returns the serialized loan with HTTP 201. | L4 and blank/delimiter-valued L5–L6 responses matched the source's semicolon-joined format. |
| `loans.csv-contract` | A | Emit loans in ID order, separated by semicolons and newline-terminated. | The list was newline-terminated; `ana;bo` appeared unescaped as an extra field. Empty-list output was not reachable through the seeded public API. |
| `loans.get-one` | A | Return one serialized loan or 404 when absent. | L1 and L6 returned HTTP 200; a missing ID returned HTTP 404. |
| `loans.list-query` | A | Query all loans in ID order. | L1–L6 were returned in order after the creates; an empty repository could not be produced through the public API. |
| `loans.list-route` | A | `GET /loans` returns plain-text rows. | HTTP 200 `text/plain` with one newline-terminated row per record. |
| `loans.return-input` | A | Route a return by loan ID and report a missing loan. | Existing and repeated-return requests returned 200; missing ID returned 404. |
| `monthly-report.spec` | C | The surviving document specifies a first-of-month report for the previous month, grouped by member, ordered by fees descending then member ID. | No implementation or runtime exists to execute; the documented schedule, columns, ordering, and omission rule are spec-derived. |
| `payment.gateway-errors` | A | Missing loans return 404; non-200 gateway responses and I/O/interruption failures map to 502. | Missing loan returned 404; the default unavailable gateway returned 502. A non-200 HTTP response and thread interruption were not separately induced. |
| `runtime.build` | A | `legacy/run.sh` packages the Maven application. | Both harness launches completed the package step successfully. |
| `runtime.launch` | A | Start the application and expose its HTTP interface. | Both launches served the endpoint and browser probes before the harness terminated them. |

## Quirks and unobserved branches

The following source behaviors match existing decision-map quirk tickets; this characterization records them without making a ruling: blank form values (#39), payment interruption (#40), repeated returns (#41), restart data reset (#42), and unescaped export fields (#43). Corresponding ledger entries link those tickets.

Two existing local drafts remain code-predicted rather than runtime-observed: `.migration/quirks/empty-loan-list-newline.md` (the seeded API has no delete operation) and `.migration/quirks/loan-id-collision.md` (a concurrent race is nondeterministic). The payment-interruption branch is likewise not inducible through the available HTTP interface; its source catch behavior remains predicted. The report does not treat any of these unobserved branches as passing runtime cases.
