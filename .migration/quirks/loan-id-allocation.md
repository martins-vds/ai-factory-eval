# Loan IDs are allocated from the row count

## Question
The source assigns each loan the ID `L` plus the current row count and one. Preserve count-based IDs, use a unique sequence, or something else?

## Evidence
- Source: `method:legacy/src/main/java/lib/LoanRepository.java:LoanRepository.lend`, `legacy/src/main/java/lib/LoanRepository.java:27-32`
- Characterization: the tier-A create probe observed `L4` with the three seeded rows; concurrent creates and gaps in IDs were not separately exercised.
- Why it looks wrong: simultaneous writes can count the same rows and try to insert the same ID; count-based allocation also does not account for gaps.

## Impact
- Ledger capabilities: `loan.create`, `data.loan-storage`
- Blocks: future migration tickets implementing these capabilities

## Options
1. Preserve exactly (IDs are count-based; tests pin this behavior)
2. Fix (the target allocates unique IDs; the divergence is recorded with this ticket as approval)
3. Other
