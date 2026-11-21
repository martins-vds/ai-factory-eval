# Empty lending fields are accepted

## Question
When `POST /loans` receives empty `member` and `isbn` form values, the source creates a loan with empty fields and returns 201. Preserve empty-field lending, reject empty fields, or something else?

## Evidence
- Source: `legacy/src/main/java/lib/LoanResource.java:37-43`
- Characterization: tier-A HTTP input `member=&isbn=` returned HTTP 201 with `L5;;;2026-11-21;2026-12-05;`
- Why it looks wrong: the ledger rule says member and isbn are required, but the implementation tests only for `null`, so empty strings pass validation.

## Impact
- Ledger capabilities: `loan.lend`
- Blocks: the validation behavior for future lend migrations

## Options
1. Preserve exactly (target accepts empty member and ISBN values; a test pins it)
2. Fix (target rejects empty values; the divergence is recorded with this ticket as approval)
3. Other
