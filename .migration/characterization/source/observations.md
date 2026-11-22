# SY-05 legacy characterization

## Source and suite

- Source: `martins-vds/ai-factory-synthetic-target`, pinned SHA `563c316ed51462b08fd6e58f3781a3c8b2890453`, path `legacy/`.
- Tier A was used for 19 executable capabilities; `docs.monthly-report` is tier C because its document states that its separate product's code and runtime are unavailable.
- No legacy test sources or test-named files were found. `legacy/run.sh` builds with `mvn -q -B package -DskipTests`.
- `.migration/characterization/source/characterize.py` recorded 31 cases: seven graph endpoints, two browser pages, 16 edge cases, two restart cases, and four payment-gateway cases. The final rerun verified all 31 goldens.
- Predicted versus observed: 30 matches and one difference. The ledger predicted a 400 response for missing `member` and `isbn`; a bodyless `POST /loans` actually returns HTTP 500 with Grizzly's HTML `Request failed.` response. Partial forms with either field missing return HTTP 400 with `member and isbn are required\n`. This difference is recorded in `.migration/quirks/bodyless-loan-create.md`.
- The request/response evidence is in `goldens/http.json`, `goldens/edges.json`, `goldens/lifecycle.json`, and `goldens/gateway.json`; browser evidence is in `goldens/browser.json`.

## Capability observations

| Capability | Tier | Prediction and observation |
|---|---:|---|
| `app.launch` | A | Predicted `run.sh` builds and launches the service; observed Maven package success and a responding app on port 8080. |
| `app.maven-build` | A | Predicted Java 17 Maven package with runtime dependencies; observed `mvn -q -B package -DskipTests` completed during the harness run. |
| `application.startup` | A | Predicted Grizzly startup and resource registration; observed `/about`, `/fees`, `/loans`, and `/payments` requests succeed or return their route-specific errors, followed by clean process termination. |
| `data.loan-storage` | A | Predicted in-memory H2 reset on startup; observed a loan created in one process was absent after restart, when the three seed loans reappeared. |
| `data.seed-records` | A | Predicted fresh startup loads L1–L3; observed exactly those three rows and their configured member, ISBN, lent, and returned dates. |
| `docs.csv-export` | A | Predicted `GET /loans` uses semicolon fields; observed sorted records with `id;member;isbn;lentOn;dueOn;returnedOn` and a trailing newline. |
| `docs.monthly-report` | C | The source document specifies a previous-calendar-month report and ordering rules; no executable code or runtime exists to observe. It remains spec-derived. |
| `fees.view` | A | Observed unknown loan 404, L2's zero fee, L3's 19-day/$4.75 fee, and L1's $10.00 cap. The seeded data does not exercise the one- or two-day waiver boundary. |
| `integration.payment-gateway` | A | Observed bodyless `POST /charge?loan=L3` to a controlled gateway and relaying of its HTTP 200 response body. |
| `library.about` | A | Observed HTTP 200 `text/html`, the packaged About content, and the expected browser heading. |
| `loan.return-date` | A | L2 initially returned on 2026-01-20; returning it replaced that value with today's date, and a repeated return returned the same current-date record. |
| `loan.return` | A | Observed a successful return response and HTTP 404 `no such loan\n` for an unknown id. |
| `loans.create` | A | Observed valid form creation as L4; partial forms return 400, blank member and ISBN values are accepted as L5, and a bodyless request returns 500. |
| `loans.due-date` | A | Observed due dates 14 days after each seeded lent date and in the created-loan response. |
| `loans.get` | A | Observed the formatted L1 record and HTTP 404 `no such loan\n` for an unknown id. |
| `loans.list` | A | Observed seeded and post-mutation rows in id order with a trailing newline. An empty table cannot be reached through the exposed API; the empty-list result remains predicted from the source implementation, not observed. |
| `loans.repository` | A | API reads, creates, and return updates were observed through the running service. Transaction rollback/close behavior is internal and was not separately forced through an externally reachable failure. |
| `loans.schema` | A | Observed id/member/ISBN/date fields in API records; empty strings persist, while missing form fields are handled at the route boundary. Database metadata was not independently introspected. |
| `loans.text-format` | A | Observed records in the predicted six-field order, separated by semicolons, with an empty final field for an unreturned loan. |
| `payment.gateway-errors` | A | Observed unknown-id 404 without a gateway call, a 503 mapped to 502 with its response body, and a refused local gateway connection mapped to 502 with `payment gateway unavailable\n`. Thread interruption itself was not separately triggered. |

## Coverage and remaining limits

JaCoCo on the 31-case suite covered 94/98 source lines, 497/513 instructions, 18/20 branches, 35/37 methods, and all 7 classes. The refreshed risk map has a maximum CRAP score of 4.0 and no method above 30; see `.migration/risk-map/SY-05.md` and `.migration/evidence/source-coverage-SY-05.md`.

The tier-A boundary did not expose a way to delete all loans or set the clock, so empty-list and one-/two-day fee-waiver cases were not directly exercised. The source-level predictions for those paths are recorded above rather than presented as observed results. Concurrent identifier collision and interrupt handling remain as decision drafts because they are not deterministic external-interface cases in this run.
