# SY-05 Legacy Characterization

Source: pinned `martins-vds/ai-factory-synthetic-target` at `563c316ed51462b08fd6e58f3781a3c8b2890453`, read-only path `legacy/`.

Tier A is available. The characterization harness starts `legacy/run.sh`, exercises HTTP and browser interfaces, and compares observations with committed goldens.

## Legacy test inventory

No Java test sources were found under the pinned `legacy/` source tree. The source package has no `src/test` directory.

## Suite

- Harness: `.migration/characterization/source/characterize.py`
- HTTP cases: 17
- Browser pages: 2
- Run journal: `.migration/evidence/runs/SY-05.md`
- HTTP golden: `.migration/characterization/source/goldens/http.json`
- Browser golden: `.migration/characterization/source/goldens/browser.json`

## Observed versus predicted

The HTTP and browser observations match the source code paths read for the characterized capabilities.

| Capability area | Input | Predicted behavior | Observed behavior | Result |
|---|---|---|---|---|
| About page | `GET /about` | HTML page with title and library details | HTTP 200, heading `About the Lending Library` | match |
| Loan list | `GET /loans` | 200 with seeded loans in semicolon format | HTTP 200, L1/L2/L3 rows | match |
| Loan get | `GET /loans/L1` | 200 loan row | HTTP 200, L1 row | match |
| Unknown loan get | `GET /loans/UNKNOWN` | 404 `no such loan` | HTTP 404, `no such loan` | match |
| Lending | `POST /loans` member/ISBN | 201 and new loan dated today | HTTP 201, L4 with 14-day due date | match |
| Missing lending fields | `POST /loans` no form fields | 400 required fields | HTTP 400, required-fields text | match |
| Empty lending fields | `POST /loans` empty strings | Source null check does not reject empty strings | HTTP 201, loan with empty member/ISBN | match; quirk |
| Return | `POST /loans/L1/return` | 200 and current return date | HTTP 200, updated L1 row | match |
| Repeated return | `POST /loans/L2/return` twice | Source overwrites the existing return date | HTTP 200 both times, current date replaces 2026-01-20 | match; quirk |
| Unknown return | `POST /loans/UNKNOWN/return` | 404 `no such loan` | HTTP 404, `no such loan` | match |
| Late-fee grace | `GET /fees/L2` | Returned within grace, no fee | HTTP 200, 0 days, $0.00 | match |
| Late-fee cap | `GET /fees/L1` | Fee calculation reaches cap | HTTP 200, $10.00 | match |
| Unknown fee | `GET /fees/UNKNOWN` | 404 text | HTTP 404, `No such loan.` | match |
| Payment success/failure | `POST /payments/L3` | Existing loan; unavailable default gateway maps IOException to 502 | HTTP 502, `payment gateway unavailable` | match |
| Unknown payment | `POST /payments/UNKNOWN` | 404 before gateway call | HTTP 404, `no such loan` | match |
| Browser About | Browser load `/about` | HTML heading | Heading `About the Lending Library` | match |
| Browser late fee | Browser load `/fees/L3` | HTML heading | Heading `Late fee for L3` | match |

## Quirks

- `.migration/quirks/loan-empty-form-values.md`
- `.migration/quirks/repeated-loan-return.md`
