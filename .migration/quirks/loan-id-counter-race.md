# Concurrent lending can generate the same loan id

## Question
Lending assigns an id from the current row count plus one, so concurrent requests can choose the same id; preserve, fix, or something else?

## Evidence
- Source: `legacy/src/main/java/lib/LoanRepository.java:27-33`
- Characterization: Source-only inference: two concurrent transactions can observe the same count and attempt the same generated id; no runtime trace was recorded in SY-04.
- Why it looks wrong: The identifier is not allocated atomically or retried after a uniqueness conflict.

## Impact
- Ledger capabilities: `loans.create`
- Blocks: Implementation decision for `loans.create` (ticket link pending orchestration).

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
