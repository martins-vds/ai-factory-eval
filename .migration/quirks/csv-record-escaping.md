# Loan records are not escaped as CSV

## Question
The source joins loan fields with semicolons but does not quote or escape field contents. Preserve the raw format, escape values, or something else?

## Evidence
- Source: `method:legacy/src/main/java/lib/LoanResource.java:LoanResource.line`, `legacy/src/main/java/lib/LoanResource.java:52-55`; `legacy/docs/export-csv.md:1-4`
- Characterization: the tier-A list probe observed semicolon-separated records; embedded semicolons, quotes, and newlines were not separately exercised.
- Why it looks wrong: a member value containing a semicolon or newline makes the documented row format ambiguous to spreadsheet consumers.

## Impact
- Ledger capabilities: `loan.record-format`, `loan.list`, `loan.get`, `loan.create`, `loan.return`
- Blocks: future migration tickets implementing these capabilities

## Options
1. Preserve exactly (raw semicolon joining; tests pin this behavior)
2. Fix (the target escapes or rejects fields that break the format; the divergence is recorded with this ticket as approval)
3. Other
