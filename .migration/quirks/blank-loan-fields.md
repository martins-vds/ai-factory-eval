# Blank loan fields are accepted

## Question
When `POST /loans` receives empty member and ISBN values, the source creates a loan with both fields blank. Preserve this, reject blank values, or something else?

## Evidence
- Source: `endpoint:legacy/src/main/java/lib/LoanResource.java:POST /loans`, `legacy/src/main/java/lib/LoanResource.java:37-43`
- Characterization: `POST /loans` with `member=` and `isbn=` returned HTTP 201 and `L5;;;2026-11-21;2026-12-05;` in the tier-A edge suite.
- Why it looks wrong: the endpoint calls these fields required but rejects only absent values, not empty values.

## Impact
- Ledger capabilities: `loan.create`
- Blocks: future migration tickets implementing loan creation

## Options
1. Preserve exactly (blank values are accepted; a test pins this behavior)
2. Fix (blank values are rejected; the divergence is recorded with this ticket as approval)
3. Other
