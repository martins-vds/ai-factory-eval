# Empty member and ISBN values create a loan

## Question
The source accepts `member=""` and `isbn=""` and creates a loan. Preserve, fix, or something else?

## Evidence
- Source: `legacy/src/main/java/lib/LoanResource.java:38-43`
- Characterization: `POST /loans` with `member=""` and `isbn=""` returned HTTP 201 and `L5;;;2026-11-21;2026-12-05;`.
- Why it looks wrong: The source checks only for `null`, so present-but-empty form values bypass the required-field refusal.

## Impact
- Ledger capabilities: `loan.lend`, `loan.csv-format`, `data.loan-storage`
- Blocks: implementation decisions for required loan form fields

## Options
1. Preserve exactly (target reproduces empty-string acceptance)
2. Fix (target refuses empty member or ISBN values)
3. Other
