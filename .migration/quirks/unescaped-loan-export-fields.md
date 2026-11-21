# Loan export fields are not escaped

## Question
`LoanResource.line` joins member and ISBN values with semicolons without escaping delimiters or newlines. Preserve this output, escape fields, or something else?

## Evidence
- Source: `method:legacy/src/main/java/lib/LoanResource.java:LoanResource.line`, `legacy/src/main/java/lib/LoanResource.java:52-55`; accepted form fields at `legacy/src/main/java/lib/LoanResource.java:37-43`
- Characterization: not separately exercised by the Analyst; source-derived prediction: a submitted member value `ana;bo` is returned as an additional semicolon-separated field.
- Why it looks wrong: the documented export has six fields per loan, but accepted values containing separators can make spreadsheet rows ambiguous.

## Impact
- Ledger capabilities: `loans.create-input`, `loans.csv-contract`, `loans.get-one`, `loans.create-response`
- Blocks: future migration tickets implementing these capabilities (not yet filed)

## Options
1. Preserve exactly (the target keeps unescaped values and pins the output)
2. Fix (the target escapes delimiters/newlines; the divergence is recorded with this ticket as approval)
3. Other
