# Concurrent loans can receive the same id

## Question
`LoanRepository.lend` derives the next id from the current row count, so concurrent requests can both choose the same id. Preserve this, use a unique id strategy, or something else?

## Evidence
- Source: `method:legacy/src/main/java/lib/LoanRepository.java:LoanRepository.lend`, `legacy/src/main/java/lib/LoanRepository.java:27-34`
- Characterization: not separately exercised by the Analyst; source-derived prediction: with three rows, two overlapping requests can both compute `L4`, and one insert can fail the primary-key constraint.
- Why it looks wrong: two valid simultaneous lending requests need not both succeed, and the result depends on transaction timing.

## Impact
- Ledger capabilities: `loans.create-persist`, `loans.create-response`
- Blocks: future migration tickets implementing these capabilities (not yet filed)

## Options
1. Preserve exactly (the target retains count-based ids and pins the collision behavior)
2. Fix (the target guarantees unique ids; the divergence is recorded with this ticket as approval)
3. Other
