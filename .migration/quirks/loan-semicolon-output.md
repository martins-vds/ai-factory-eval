# Loan fields are not escaped in semicolon output

## Question
When a member or ISBN contains a semicolon or newline, the source inserts it raw into the six-field loan line; preserve this, escape it, or something else?

## Evidence
- Source: `method:legacy/src/main/java/lib/LoanResource.java:LoanResource.line`, `legacy/src/main/java/lib/LoanResource.java:52-55`
- Characterization: predicted from source pending tier-A confirmation: a member value `a;b` is returned as an extra field in the semicolon-separated loan line.
- Why it looks wrong: `legacy/docs/export-csv.md:3` defines a semicolon-separated six-field format used by spreadsheets, but raw values can change its field count.

## Impact
- Ledger capabilities: `loan.list`, `loan.get`, `loan.lend`, `loan.return`
- Blocks: future migration tickets implementing these capabilities (not yet filed)

## Options
1. Preserve exactly (emit unescaped fields; tests pin this behavior)
2. Escape or reject delimiter/newline values (record the divergence with this ticket as approval)
3. Other
