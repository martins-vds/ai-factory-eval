# Empty loan fields are accepted

## Question
When `POST /loans` receives an empty `member` or `isbn` value, the source accepts it because it rejects only null values. Preserve this, reject blank values, or something else?

## Evidence
- Source: `endpoint:legacy/src/main/java/lib/LoanResource.java:POST /loans`, `legacy/src/main/java/lib/LoanResource.java:38-42`
- Characterization: the tier-A HTTP suite exercised valid form values; empty values were not separately exercised.
- Why it looks wrong: a loan with an empty member or ISBN can be persisted even though the fields identify its borrower and book.

## Impact
- Ledger capabilities: `loan.create`
- Blocks: future migration tickets implementing this capability

## Options
1. Preserve exactly (empty strings are accepted; tests pin this behavior)
2. Fix (the target rejects blank values; the divergence is recorded with this ticket as approval)
3. Other
