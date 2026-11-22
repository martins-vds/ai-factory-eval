# Concurrent loan creation can choose the same id

## Question
The source derives each new loan id from the current row count; preserve this sequential id scheme under concurrent requests, add serialization, or something else?

## Evidence
- Source: `method:legacy/src/main/java/lib/LoanRepository.java:LoanRepository.lend`, `legacy/src/main/java/lib/LoanRepository.java:27-34`
- Characterization: tier A observed sequential L4, L5, and L6 creation. A concurrency race was not induced; source prediction is that simultaneous requests can both read the same count and choose the same id.
- Why it looks wrong: concurrent lending can contend for the same primary key and fail one request.

## Impact
- Ledger capabilities: `loan.lend`, `data.loan-storage`
- Blocks: future migration tickets implementing these capabilities (not yet filed)

## Options
1. Preserve exactly (derive ids from row count; tests pin concurrent conflict behavior)
2. Use a collision-safe id allocation strategy (record the sequential-id change with this ticket as approval)
3. Other
