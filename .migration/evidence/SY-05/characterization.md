# SY-05 — source characterization

- Source: `martins-vds/ai-factory-synthetic-target@563c316ed51462b08fd6e58f3781a3c8b2890453`
- Tier: A for 18 capabilities; C for `reporting.monthly-report`
- Suite: 19 HTTP cases, 2 browser-page cases, 2 gateway cases, and 2 fee-boundary cases
- Result: 25/25 cases passed; 25 predictions matched, 0 differed
- Run journal: `.migration/evidence/runs/SY-05.md`
- Goldens: `.migration/characterization/source/goldens/{http,browser,gateway,fee-boundaries}.json`

The harness builds the pinned read-only source in a temporary copy. Its two-day and three-day fee
fixtures are appended only to that copy's compiled seed resource. The pinned checkout was not modified.
The source contains no `src/test` tree or legacy test files.

## Observed versus predicted

Predictions below are from the pinned source implementation and the existing capability boundaries.
Each observation matched its prediction; complete requests and responses are in the linked goldens.
Dates below are from the 2026-11-22 run.

| Case | Predicted | Observed |
|---|---|---|
| About page | `GET /about` returns the public library HTML, 200 | 200 HTML with name, Monday–Saturday hours, 14-day lending period, and contact |
| Fee for L1 | The returned date is absent, so use today; floor late days at zero and cap fee at $10 | 310 days late; $10.00; 200 HTML |
| Fee for L2 | Early return gives zero late days and no fee | 0 days late; $0.00; 200 HTML |
| Fee for L3 | 19 days late gives 17 chargeable days at $0.25 | 19 days late; $4.75; 200 HTML |
| Fee for unknown ID | Unknown loan returns 404 HTML | 404, `<p>No such loan.</p>` |
| Seeded list | Startup inserts L1–L3; list is ID-ordered, newline-terminated, six semicolon fields per row | L1, L2, L3 in order; L1's empty returned date is the final field |
| Lookup L1 | Existing loan returns one formatted line, 200 | `L1;ana;9780134685991;2026-01-02;2026-01-16;` |
| Lookup unknown ID | Unknown loan returns 404 text | 404, `no such loan` |
| Lend valid fields | Non-null fields create the next ID, dated today, due in 14 days; return 201 | L4, due 2026-12-06; 201 |
| Lend missing ISBN | Missing required form value returns 400 | 400, `member and isbn are required` |
| Lend missing member | Missing required form value returns 400 | 400, `member and isbn are required` |
| Lend empty fields | Empty strings pass the null-only check and are persisted | L5 with empty member and ISBN; 201 |
| Lend semicolon fields | Loan fields are joined without escaping; embedded delimiters remain in output | L6 output contains `L6;one;two;isbn;test;...`; 201 |
| List after lending | Reads include the new loans and preserve ID ordering | L1–L6 returned, including L5's empty fields and L6's unescaped delimiters |
| Return L1 | Existing loan receives today's return date; 200 | L1's returned date becomes 2026-11-22 |
| Return already-returned L2 | A repeated return replaces the previous return date with today | L2's prior 2026-01-20 date becomes 2026-11-22; 200 |
| Return unknown ID | Unknown loan returns 404 text | 404, `no such loan` |
| Pay unknown ID | Loan lookup precedes the gateway call | 404, `no such loan` |
| Pay with unavailable default gateway | I/O failure maps to 502 with the unavailable message | 502, `payment gateway unavailable` |
| Browser `/about` | Page navigation succeeds and exposes the About heading | 200; heading `About the Lending Library` |
| Browser `/fees/L3` | Page navigation succeeds and exposes the fee heading | 200; heading `Late fee for L3` |
| Local gateway success | Source POSTs to `/charge?loan=L3` with no body; gateway 200 maps to 200 | Captured POST and empty body; source returns 200, `charged` |
| Local gateway non-200 | A non-200 gateway response maps to 502 and preserves its body | Gateway 402 `declined` maps to 502, `declined` |
| Fee exactly 2 days late | The waiver includes the two-day boundary | 200 HTML; 2 days late; $0.00 |
| Fee exactly 3 days late | The first chargeable day is billed at $0.25 | 200 HTML; 3 days late; $0.75 |

The local gateway and boundary fixtures are test-only inputs in the temporary source copy. These
observations exercise the source application's real HTTP handling; they do not replace its code or
the default-seed observations.

## Ledger coverage and tier

| Capability | Tier | Evidence and scope |
|---|---|---|
| `application.build` | A | `run.sh` packages the source without tests and starts the app successfully. |
| `application.startup` | A | Default-port startup served all seven graph endpoints; the custom `PORT` startup served the gateway and fee probes. |
| `data.loan-schema` | A | Seeded and created loans were returned through the API with six fields; omitted fields were rejected and empty strings were persisted. |
| `data.loan-storage` | A | A second application process exposed only the three seeds after the first process created L4–L6; see the restart quirk draft. |
| `data.seed-records` | A | Initial `GET /loans` returned the three seeded rows L1–L3. |
| `fees.calculate` | A | L2, L3, L1, and controlled exactly-two/exactly-three-day returns cover floor, waiver, accrual, and cap. |
| `fees.page` | A | Existing, early, late, overdue, and unknown loans returned the expected HTML and status. |
| `integration.payment-gateway` | A | Local gateway requests captured method, path, and empty body; success and non-200 responses were exercised. |
| `library.about` | A | HTTP and browser observations include the page body and heading. |
| `loan.due-date` | A | Seeded and newly created loans are due 14 days after `lentOn`. |
| `loan.export-format` | A | Loan list/lookup and delimiter-containing member/ISBN values establish the six-field semicolon format and unescaped delimiters. |
| `loan.lend` | A | Valid, missing-field, empty-field, and delimiter-field requests were observed. |
| `loan.list` | A | Seed and post-write lists establish ordering, newline termination, and persisted rows in one process. |
| `loan.lookup` | A | Existing and unknown IDs returned the specified status and body. |
| `loan.return-date` | A | An already-returned L2's 2026-01-20 return date was overwritten by today's date. |
| `loan.return` | A | Existing, already-returned, and unknown loan requests were observed. |
| `loan.transactions` | A | Successful create/return writes were read back; unknown return caused no persisted row. Transaction rollback/close internals are not separately observable through the HTTP boundary. |
| `payment.gateway-errors` | A | Unknown-loan 404, unavailable-gateway 502, and gateway non-200 502 responses were observed. |
| `reporting.monthly-report` | C | The source runtime is absent; the only source is the specification in `legacy/docs/reports-spec.md:1-8`. See the worked example below. |

The graph risk-map hotspots (`LateFeeView.page` and `FinePayments.pay`, CRAP 20 each) were
characterized with boundary, missing-resource, unavailable-gateway, successful-gateway, and
non-200-gateway cases. The source has no legacy tests. HTTP-observable error paths were exercised;
the interruption-only branch in `FinePayments.pay` cannot be induced via its HTTP interface and
remains explicitly identified in `.migration/quirks/payment-interrupt.md`.

### Tier-C worked example: monthly reporting

Source `legacy/docs/reports-spec.md:1-8` predicts that a report run on the first day of a month
covers the prior month, emits one row per member with loans started, late returns, and late fees
in cents, sorts by fees descending then member ID, and omits members with no loans. The document is
the complete remaining specification; no reporting implementation or runtime exists to execute.
This capability is therefore `spec-derived`, not runtime-characterized.
