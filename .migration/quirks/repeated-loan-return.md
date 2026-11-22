# Repeated return changes the return date

## Question
When `POST /loans/{id}/return` is called for a loan that is already returned, the source replaces `returnedOn` with today's date. Preserve this, reject repeat returns, or something else?

## Evidence
- Source: `method:legacy/src/main/java/lib/LoanRepository.java:LoanRepository.markReturned`, `legacy/src/main/java/lib/LoanRepository.java:36-44`; route `legacy/src/main/java/lib/LoanResource.java:45-50`
- Characterization: tier A observed L2 initially returned on 2026-01-20; the first `POST /loans/L2/return` replaced the date with 2026-11-22, and a second call returned the same updated record. See `.migration/characterization/source/goldens/edges.json`.
- Why it looks wrong: repeating the request changes the historical return date and can change the late fee shown for that loan.

## Impact
- Ledger capabilities: `loan.return-date`, `loan.return`
- Blocks: future migration tickets implementing these capabilities (not yet filed)

## Options
1. Preserve exactly (repeated returns overwrite the date; tests pin this behavior)
2. Fix (the target does not overwrite the date; the divergence is recorded with this ticket as approval)
3. Other
