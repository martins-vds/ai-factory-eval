# Characterization — SY-05 (tier-A suite and tier-C specification)

- Source: `martins-vds/ai-factory-synthetic-target` at `563c316ed51462b08fd6e58f3781a3c8b2890453`, source path `legacy`.
- The writable `legacy/` run copy and pinned `.source` subtree have the same tree `1e683e0091beb079121c2ab6d223573ae29186ae`; `.source/legacy` was not modified.
- Tier-A command: `.migration/harness/tools/afs-run --ticket SY-05 --name source-characterization-verify -- python .migration/characterization/source/characterize.py`.
- Result: pass; 23 HTTP observations and 2 browser-page observations matched their normalized goldens. See `.migration/evidence/runs/SY-05.md` and `.migration/characterization/source/goldens/`.
- The source tree has no legacy test sources or test graph edges; no legacy tests were available to inventory.
- The source graph gate passed with 86 nodes, 119 edges, 8 entry points, and 67 enriched edges. The About route and static page do not reach a data table, as expected for static information.

## Predicted vs observed

| Capability | Prediction from source/docs | Observation | Result |
|---|---|---|---|
| `application.build` | `run.sh` packages the Java app and launches `lib.App`. | The source built and started for both characterization runs. | Match |
| `application.startup` | The process uses PORT (default 8080), registers four resources, and shuts down the server and entity manager factory. | The source became ready for both runs; all probes completed. | Match |
| `data.loan-storage` | Reads/writes persist within the running process; startup recreates the in-memory database. | L4–L6 and a changed L2 return date appeared before restart; after restart only the original seed records remained. | Match |
| `data.seed-records` | Startup loads L1–L3. | Initial and restarted loan listings contained the same three seeds. | Match |
| `repository.transactions` | Reads close their entity manager; writes commit and close it, rolling back if a transaction remains active after failure. | Read and write operations through list, create, and return succeeded. A transaction failure was not triggerable through the source interfaces. | Match for exercised operations |
| `loan.list` | GET `/loans` returns loans ordered by id, one text row per record, with a final newline. | Seed and newly created loan listings matched the order and newline behavior. | Match |
| `loan.text-export` | Rows contain id, member, ISBN, lent date, due date, and return date separated by raw semicolons. | A member containing `;` and ISBN containing a newline were returned without escaping; the export split the record into ambiguous text lines. | Match; existing quirk #43 confirmed |
| `loan.get` | A known id returns its row; an unknown id returns 404. | L1 returned 200; an unknown id returned `no such loan` with 404. | Match |
| `loan.lend` | Valid non-null form values return 201; absent values return 400; blank strings are not rejected. | Valid values returned L4; an empty form and either missing field returned 400; two empty strings created L5 with 201. A request with no body/content type returned a Grizzly 500 before handler validation, differing from the handler-level 400 prediction. | One difference; existing quirk #39 and new draft |
| `loan.return` | An existing loan returns 200 with its updated row; an unknown id returns 404. | L1 returned 200; an unknown id returned 404. | Match |
| `loan.return-date` | A return request overwrites `returnedOn` with today's date, including for an already-returned loan. | Seed L2 changed from `2026-01-20` to `2026-11-22`; its late fee changed from $0.00 to $10.00. | Match; existing quirk #41 confirmed |
| `loan.due-date` | Due date is 14 days after the lent date. | Listed rows and fee pages showed the expected 14-day dates. | Match |
| `fees.calculation` | Late days are clamped at zero; up to two days late is waived, otherwise fees are 25 cents/day capped at $10. | L3 showed 19 days/$4.75, L1 showed the $10 cap, L2 before its repeated return showed $0.00, and after the repeated return it showed $10.00. The exact two-day boundary cannot be driven because the API accepts no dates. | Match for observed cases; boundary limitation recorded |
| `fees.page` | GET `/fees/{id}` renders a heading, due/late text, and a two-decimal fee; an unknown id returns 404 HTML. | The fee page and browser heading matched; an unknown id returned `<p>No such loan.</p>` with 404. | Match |
| `integration.payment-gateway` | Existing-loan payments POST to the configured gateway; HTTP 200 maps to 200, other responses and I/O/interruption failures map to 502. | L3 returned 502 with `payment gateway unavailable`; unknown id returned 404. No real gateway was available, so success, non-200 gateway replies, and interruption were not exercised. | Match for observed cases |
| `about.page` | GET `/about` serves the static library information page. | HTTP returned the page and the browser observed the expected heading. | Match |
| `reports.monthly-spec` | The document specifies prior-month aggregates sorted by fees descending then member id, omitting members without loans. | The document states no report code or runtime is available. The approved plan includes it as a management command, so it is recorded as spec-derived tier C rather than claiming tier-A behavior. | Spec-derived; no executable source |

The 25 tier-A observations comprise the 23 HTTP observations and two browser pages. Twenty-four matched source-derived predictions; the single difference was a POST without form content type reaching Grizzly's 500 response instead of handler-level 400. The documentation-only report is characterized separately at tier C.

## Existing quirks and new draft

- `martins-vds/ai-factory-synthetic-target#39` — blank member and ISBN values are accepted; observed.
- `martins-vds/ai-factory-synthetic-target#40` — interruption is not separately exercised.
- `martins-vds/ai-factory-synthetic-target#41` — repeated return overwrites the date and changes the fee; observed.
- `martins-vds/ai-factory-synthetic-target#42` — restart resets data; observed after creating and updating loans.
- `martins-vds/ai-factory-synthetic-target#43` — export delimiters are not escaped; observed.
- `.migration/quirks/loan-create-missing-content-type.md` — no form content type returns a Grizzly 500; observed.

The live decision map records rulings for quirks #39–#43; this characterization records source behavior without changing those decisions. An empty database, transaction rollback after failure, exact two-day fee boundary, successful gateway response, and payment interruption could not be produced through available source interfaces. No mocks or source edits were used.
