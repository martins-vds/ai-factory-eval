# Loan export does not escape semicolons

## Question
When a loan field contains a semicolon, the source emits it unescaped in the semicolon-separated export. Preserve this, escape the field, or something else?

## Evidence
- Source: `method:legacy/src/main/java/lib/LoanResource.java:LoanResource.line`, `legacy/src/main/java/lib/LoanResource.java:52-55`; contract: `legacy/docs/export-csv.md:3-4`
- Characterization: tier A observed member `one;two` and ISBN `isbn;test` emitted unescaped as `L6;one;two;isbn;test;2026-11-22;2026-12-06;`; see `.migration/characterization/source/goldens/http.json` (`lend-delimiter-fields`) and `.migration/evidence/SY-05/characterization.md`.
- Why it looks wrong: an embedded delimiter can make spreadsheet consumers parse a loan as more than six fields.

## Impact
- Ledger capabilities: `loan.export-format`
- Blocks: future migration tickets implementing this capability (not yet filed)

## Options
1. Preserve exactly (fields are not escaped; a test pins this behavior)
2. Fix (escape or reject delimiter-containing values; record the approved divergence in the ledger)
3. Other
