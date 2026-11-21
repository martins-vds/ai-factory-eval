# An empty loan list contains a newline

## Question
`LoanResource.list` appends a newline even when there are no loans, so the empty response is one newline byte. Preserve this, return an empty body, or something else?

## Evidence
- Source: `method:legacy/src/main/java/lib/LoanResource.java:LoanResource.list`, `legacy/src/main/java/lib/LoanResource.java:25-28`
- Characterization: not separately exercised by the Analyst; source-derived prediction: an empty repository result produces `"\n"` because the joining operation has an empty prefix and a newline suffix.
- Why it looks wrong: a client exporting an empty collection receives a blank line rather than an empty response.

## Impact
- Ledger capabilities: `loans.list-query`, `loans.csv-contract`
- Blocks: future migration tickets implementing these capabilities (not yet filed)

## Options
1. Preserve exactly (the target returns the trailing newline for an empty list)
2. Fix (the target returns an empty body; the divergence is recorded with this ticket as approval)
3. Other
