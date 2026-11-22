# Source characterization — SY-05

## Environment and test inventory

- Source: `martins-vds/ai-factory-synthetic-target`, SHA `563c316ed51462b08fd6e58f3781a3c8b2890453`, path `legacy`.
- Tier A: the source Maven build and Grizzly server ran; HTTP, browser, mutation, and restart probes were executed against the source. Captured observations are in `goldens/`.
- No legacy test sources or test files were present under `legacy/`; the source graph also has zero `tested_by` edges.

## Predicted and observed behavior

The source predictions below were derived from the pinned code, the source documents, and the domain graph. The 22 executable HTTP/browser/restart observations matched those predictions; no observed-vs-predicted differences were found.

| Capability | Prediction | Observation |
|---|---|---|
| `loan.list` | List loans in ascending id order as six semicolon-separated fields, ending each row with a newline. | L1–L3 were returned in order with the documented fields and trailing newlines; the post-mutation list exposed the raw semicolon in a member value. |
| `loan.get` | Return one formatted loan or `404` with `no such loan\n`. | L1 returned its row; an unknown id returned the expected `404` body. |
| `loan.lend` | Missing form parameters return `400`; valid values create a loan dated today and due 14 days later. | Missing fields returned `400`; `dee`/`123` created L4 with a 14-day due date. Empty strings were accepted as L5 (`201`), and `a;b` was emitted unescaped as L6. Concurrent id allocation was not exercised; the source derives ids from row count. |
| `loan.return` | Returning a known loan records today's date; an unknown id returns `404`. | L1 returned `200` with today's date; an unknown id returned `404`. A repeat return also returned `200`. |
| `loan.return-date` | The return date is visible in loan output and used by fee calculation. | L1's updated date appeared in the list and was reset to empty after restart. The repeat-return probes ran on the same day, so they confirm acceptance but do not distinguish a date overwrite. |
| `loan.due-date` | Due date is 14 days after `lentOn`. | Seed and newly created loan output showed the expected due dates. |
| `fees.view` | Calculate from the due date to `returnedOn` or today; waive up to two late days and cap at $10. | L3 rendered 19 days late and `$4.75`; new L4 rendered zero late days and `$0.00`; an unknown id returned `404`. Exact waiver and cap boundaries were not reachable through the public source API. |
| `integration.payment-gateway` | Look up the loan, call the configured/default gateway, then return its result. | Existing L3 reached the default `.invalid` gateway and returned `502`; an unknown loan returned `404`. No live gateway success path was available, and no stand-in was used. |
| `payment.gateway-errors` | Map gateway I/O or interruption failures to `502`. | The unavailable-gateway path returned `502` and `payment gateway unavailable\n`. An actual thread interruption was not induced. |
| `library.about` | Serve the static public information as HTML. | HTTP returned `200`/`text/html`; Chromium observed the expected About heading. |
| `data.loan-storage` | Store loan fields in the source LOAN table and retain changes only for the process lifetime. | Created L4 and returned L1 were visible during the process; after restart only seed rows remained and L1's returned date was empty. |
| `data.seed-records` | Load L1, L2, and L3 on startup. | The three expected rows were present at initial startup and after restart. |
| `application.startup` | `run.sh` builds the Java app and starts Grizzly on the configured/default port. | The existing tier-A harness successfully built and started the source for both process runs. |
| `reports.monthly` | The document specifies a first-of-month prior-month report, one row per member with activity, sorted by fees descending then member id. | No reporting code or runtime exists in the source; this capability is characterized from the document only (tier C). |

The public API cannot create an empty loan table or choose arbitrary lending/return dates. Consequently, the exact two-day waiver, fee cap, and return-date overwrite across different dates remain source-predicted rather than tier-A-observed. The default payment gateway is unavailable, so its successful response mapping also remains unobserved.

## Suite

- `characterize.py --record`: recorded 7 source endpoints, 11 edge cases, 2 restart cases, and 2 browser pages (22 observations).
- `characterize.py`: verified all 22 observations against the stored goldens.
- The committed run journal `.migration/evidence/runs/SY-05.md` contains the exact commands and outputs.
