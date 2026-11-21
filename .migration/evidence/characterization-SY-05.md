# SY-05 legacy characterization

- Issue: martins-vds/ai-factory-eval#2137
- Source: `martins-vds/ai-factory-synthetic-target@563c316ed51462b08fd6e58f3781a3c8b2890453`, `legacy/`
- Runtime tier: A for 15 executable capabilities; C / spec-derived for `reports.monthly`.
- Harness: `.migration/characterization/source/characterize.py`; HTTP goldens: `.migration/characterization/source/goldens/http.json`; browser goldens: `.migration/characterization/source/goldens/browser.json`.
- Run journal: `.migration/evidence/runs/SY-05.md`.

## Legacy test inventory

The pinned `legacy/` tree contains no `src/test` directory and no test source files. The source graph has zero `tested_by` edges. `legacy/run.sh` packages with `-DskipTests`; the characterization harness is the executable suite used here.

## Observed versus predicted

The final harness run verified 23 HTTP request/response cases and 2 browser-page cases. All 25 executable cases matched the prediction from the source: 25 matches, 0 differences.

| Capability | Predicted behavior | Observed behavior |
|---|---|---|
| `fees.view` | Found loans render fee details; missing loans return 404 HTML. | L3 rendered 19 days and `$4.75`; L1 rendered 309 days and the `$10.00` cap; L2 rendered 0 days and `$0.00` before its repeated return; missing loan returned 404. After the repeated return L2 rendered 301 days and `$10.00`. Browser heading for L3 was `Late fee for L3`. |
| `library.about` | `/about` serves the static HTML page. | HTTP returned 200 `text/html` with the opening-hours, loan-period and contact text; Chromium saw heading `About the Lending Library`. |
| `loans.create` | Both form parameters are needed; otherwise return 400. Non-null values create a loan dated today. | `dee` / `123` created L4 with lent date 2026-11-21 and due date 2026-12-05. Omitting either field returned 400 and `member and isbn are required`. Both fields empty created L5 with 201 and empty member/ISBN values. |
| `loans.due-date` | Due date is 14 calendar days after lending. | L4's 2026-11-21 lent date produced 2026-12-05; seeded dates also matched the 14-day rule. |
| `loans.get` | Found IDs return one formatted line; missing IDs return 404. | L1 and created L4 returned 200; `missing` returned 404 and `no such loan`. |
| `loans.list` | Startup seeds are ID-ordered, each line ends with a newline; writes appear during the process. | Initial list contained L1–L3 in order. Later list included L4 and empty-valued L5. After restarting the process, the list contained only the original L1–L3 seeds. |
| `loans.record-format` | Fields are joined by semicolons, with an empty final field for an unreturned loan. | Normal and newly created loans had the six-field form; an `m;delim` member was emitted unescaped as `L6;m;delim;123;2026-11-21;2026-12-05;`, producing an extra apparent field. |
| `loans.return` | Found loans receive today's return date; missing IDs return 404. | Returning L1 set `returnedOn` to 2026-11-21; an unknown ID returned 404. Re-returning seeded L2 replaced its prior 2026-01-20 date with 2026-11-21. |
| `loans.schema` | The LOAN record has the declared ID/member/ISBN/lent/returned fields; return date may be null. | Seed and response lines exposed those fields and the empty unreturned field; no direct database constraint violation was induced through the public API. |
| `loans.seed-data` | Startup loads L1–L3 with the declared initial values. | The initial list showed all three rows and their dates. The restart list restored those rows and discarded the in-process L4–L6 changes. |
| `payments.charge` | Unknown loans return 404; an unavailable gateway maps to 502. | Unknown ID returned 404 before contacting the gateway. L3 with the default `.invalid` gateway returned 502 and `payment gateway unavailable`. No live success-path gateway was available to exercise. |
| `reports.monthly` | The remaining document specifies a previous-month report, one row per member, fee-descending/member-ID ordering and omission of members without loans. | No executable implementation or runtime exists in the pinned source; this is spec-derived only, not a runtime observation. |
| `runtime.application` | The app starts on the default port and registers the four resources. | `legacy/run.sh` started the service on port 8080; the HTTP and browser cases reached the registered routes. Both processes shut down after the suite. |
| `runtime.build-launch` | Maven packages with tests skipped, then launches `lib.App`. | The harness successfully built and launched the service twice through `legacy/run.sh`. No legacy tests were available to run. |
| `storage.persistence-config` | Startup uses in-memory H2, drop-and-create schema generation and the seed script. | Each process start served L1–L3; restarting restored those rows and discarded the preceding process's changes. |
| `storage.repository-transactions` | Successful writes commit and reads return the written entity; failed writes roll back if a transaction remains active. | Create/read and return/list sequences showed successful writes persisted within a process. Rollback and manager-cleanup internals were not directly observable through the public interface. |

## Coverage and limits

The JaCoCo run covered 93/98 source lines and 482/513 instructions. The refreshed coverage-aware risk map is `.migration/risk-map/SY-05.md`; its maximum CRAP score is 4.0 and no method exceeds 30.

The source always seeds three records and has no delete route, so an empty-list state cannot be reached through its public interface. The exact two-day late-fee boundary is not reachable with the fixed seed dates and source-owned current clock. The default payment host is unavailable; the gateway 200/non-200 response branches were not exercised against a live gateway. The source provides no public seam to force repository rollback. These unobserved internals are distinguished from the observed responses above; no stand-in service was introduced.

## Quirk drafts

- `.migration/quirks/empty-loan-fields-accepted.md` — an empty member and ISBN are accepted as a successful loan.
- `.migration/quirks/loan-export-unescaped-delimiters.md` — observed delimiter value is emitted without escaping.
- `.migration/quirks/return-date-overwrite.md` — repeated return replaces the prior date and changes the fee calculation.
- `.migration/quirks/restart-data-loss.md` — process restart restores the seed-only in-memory database.
- Existing source-only drafts remain for ID allocation concurrency, gateway ID encoding, gateway interruption and the monthly report's absent runtime.
