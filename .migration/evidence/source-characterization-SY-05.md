# SY-05 — legacy source characterization

- Source: `martins-vds/ai-factory-synthetic-target@563c316ed51462b08fd6e58f3781a3c8b2890453`
- Ledger scope: 16 capabilities; 15 characterized at tier A and one spec-derived at tier C.
- Legacy tests: no Java test sources exist under `legacy/src/test`; the source graph also has no `tested_by` edges.

## Suite and coverage

The existing source harness was extended and run against `legacy/run.sh`. The verified suite contains 26 HTTP requests (seven graph endpoints plus 19 additional error, edge, persistence, and restart cases), four captured gateway requests, and two browser pages. All 32 observations matched their recorded goldens. See `.migration/characterization/source/goldens/http.json`, `gateway.json`, and `browser.json`; the exact run logs are identified by `.migration/evidence/runs/SY-05.md`.

JaCoCo observed 497/513 instructions, 94/98 lines, 18/20 branches, 35/37 methods, and 7/7 classes covered. The refreshed complexity/coverage map is `.migration/risk-map/SY-05.md`. The hottest methods, `LateFeeView.page` and `FinePayments.pay`, each have 100% line coverage in this run.

## Predicted versus observed

For each executable capability, the prediction is the ledger boundary/rules at the pinned source. A match means the observed external behavior agrees; it does not mean every theoretically possible input was reachable. The monthly report is documentation-only, so it has a spec-derived example rather than a runtime observation.

| Capability | Tier | Prediction | Observation | Result |
|---|---|---|---|---|
| `about.page` | A | Public page contains the library name, hours, loan period, and contact. | `GET /about` returned HTTP 200 HTML with all four items. | Match |
| `application.build-run` | A | `legacy/run.sh` builds with Maven and starts `lib.App`. | The harness ran `legacy/run.sh` twice; both launches became HTTP-ready on the default port. | Match |
| `application.startup` | A | Default port 8080; loan, fee, payment, and about resources are registered and the process can stop. | Default-port `/about`, loan list/get/create/return, fee, and payment routes responded; both launched processes exited after termination. | Match |
| `data.loan-entity` | A | Loan fields persist; `dueOn` is `lentOn + 14 days`, and `returnedOn` may be null. | Seed and created records showed due dates 14 days after lending; an unreturned record had an empty final field. | Match |
| `data.loan-storage` | A | H2 initializes from seeds and writes are visible during the process. | The three seeds loaded and a created loan was retrievable. After restart, the runtime-created `L4` returned 404 and only the seed rows remained. Successful writes were exercised; rollback-on-failure was not forced. | Match |
| `data.seed-records` | A | Startup inserts L1/ana, L2/bo, and L3/cy with their pinned dates and ISBNs. | The initial ordered list contained those exact three records and values. | Match |
| `fees.view` | A | Known loans return fee HTML; an unknown ID returns 404; late days are nonnegative, waived through two days, then charged at 25 cents/day up to $10. | L1 (unreturned, 310 days late) returned $10.00; L2 (returned before due) returned 0 days/$0.00; L3 (19 days late) returned $4.75; unknown returned 404. | Match |
| `loan.create` | A | Missing fields return 400; valid fields create today’s loan with count-based ID. | Missing member or ISBN separately returned 400. Valid input created L4. Empty member and empty ISBN each returned 201 (L5 and L6); semicolon member input created L7 without escaping. | Match; quirks confirmed |
| `loan.get` | A | Known ID returns its formatted record; unknown ID returns 404. | L1 returned HTTP 200 with a final newline; unknown returned HTTP 404 `no such loan`. | Match |
| `loan.list` | A | All rows are ordered by ID and end with a newline. | Initial rows were L1, L2, L3 in order with a final newline. The seeded startup prevents observing an empty list through the public interface. | Match |
| `loan.record-format` | A | Six fields are joined by semicolons; an unreturned date is empty. | The record ended with an empty returned-date field; member `gray;lee` appeared unquoted in L7, producing an ambiguous row. | Match; quirk confirmed |
| `loan.return-date` | A | A return writes today’s date even when a prior return date exists. | Returning L2 replaced its seed date `2026-01-20` with `2026-11-22`; repeating the operation returned the same current date. | Match; quirk confirmed |
| `loan.return` | A | Known ID returns the updated record; unknown ID returns 404. | L1 returned HTTP 200 with today’s date; unknown returned HTTP 404 `no such loan`. | Match |
| `payment.gateway-errors` | A | Gateway I/O errors map to HTTP 502 `payment gateway unavailable`; non-200 gateway statuses map to 502 with the upstream body. | A controlled localhost gateway connection close returned 502 `payment gateway unavailable`; upstream 503 returned 502 with `gateway failure`. `InterruptedException` itself was not induced. | Match for observed errors |
| `payments.charge` | A | Existing loan sends a bodyless POST to `/charge?loan={id}`; success maps to 200, other status to 502; unknown ID skips the gateway. | L1 returned 200 twice and produced two bodyless requests to `/charge?loan=L1`; L2’s 503 mapped to 502; unknown loan returned 404 with no gateway request. | Match; repeat-charge quirk confirmed |
| `reporting.monthly-spec` | C | First-of-month run covers the preceding month; rows include member, started loans, late returns, and fees, sorted by fees descending then member ID; members with no loans are omitted. | No report implementation/runtime exists. The only source artifact is `legacy/docs/reports-spec.md`; a spec-derived example is given below, not represented as a runtime observation. | Spec-derived; no runtime comparison |

### Spec-derived example for `reporting.monthly-spec`

For a report run on 2026-03-01, assume the prior-month aggregate has member `b` with `(2 started, 1 late return, 25 cents)`, member `a` with `(1 started, 1 late return, 25 cents)`, and member `c` with no February loans. The documented output contains `a` then `b` (fee tie broken by member ID) and omits `c`. This is a worked interpretation of `legacy/docs/reports-spec.md:6-9`, not observed program output.

## Coverage limits and quirks

- Fixed seed data and the public API do not allow setting arbitrary loan dates, so exact two-/three-day fee boundaries were not reachable; zero-late, positive-late, and capped cases were observed.
- There is no delete route, so the public interface cannot produce an empty loan list.
- Count-ID concurrency/gaps, a forced database rollback, and a gateway `InterruptedException` were not induced. The source code and pre-existing quirk drafts describe those unresolved cases.
- Existing quirk drafts were updated with the observations for empty fields, raw semicolon formatting, repeated returns, repeated charges, and restart data loss. No new quirk was discovered; no quirk was resolved here.
