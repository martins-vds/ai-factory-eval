# Loan export does not escape semicolons

## Question
When a loan field contains a semicolon, the source emits it unescaped in the semicolon-separated export. Preserve this, escape the field, or something else?

## Evidence
- Source: `method:legacy/src/main/java/lib/LoanResource.java:LoanResource.line`, `legacy/src/main/java/lib/LoanResource.java:52-55`; contract: `legacy/docs/export-csv.md:3-4`
- Characterization: tier A is established in `.migration/references/characterization.md`; delimiter-containing fields were not separately exercised.
- Why it looks wrong: an embedded delimiter can make spreadsheet consumers parse a loan as more than six fields.

## Impact
- Ledger capabilities: `loan.export-format`
- Blocks: future migration tickets implementing this capability (not yet filed)

## Options
1. Preserve exactly (fields are not escaped; a test pins this behavior)
2. Fix (escape or reject delimiter-containing values; record the approved divergence in the ledger)
3. Other
