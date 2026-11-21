# Repeated returns overwrite the return date

## Question
Each return request writes the current date even when a loan is already returned, so a later repeat changes `returnedOn`; preserve, fix, or something else?

## Evidence
- Source: `legacy/src/main/java/lib/LoanResource.java:47-49`; `legacy/src/main/java/lib/LoanRepository.java:36-43`
- Characterization: Source-only inference: returning a loan on a later date replaces its prior `returnedOn` with the later date; no runtime trace was recorded in SY-04.
- Why it looks wrong: A return operation commonly records the first return date, but the source does not distinguish an already-returned loan.

## Impact
- Ledger capabilities: `loans.return`
- Blocks: Implementation decision for `loans.return` (ticket link pending orchestration).

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
