# Repeated return changes the return date

## Question
When `POST /loans/{id}/return` is called for a loan that is already returned, the source replaces `returnedOn` with today's date. Preserve this, reject repeat returns, or something else?

## Evidence
- Source: `method:legacy/src/main/java/lib/LoanRepository.java:LoanRepository.markReturned`, `legacy/src/main/java/lib/LoanRepository.java:36-44`; route `legacy/src/main/java/lib/LoanResource.java:45-50`
- Characterization: tier A observed a repeat return of L1 returning HTTP 200 with today's date (`goldens/edges.json`, `repeat-return`). Both calls ran on the same day, so the date overwrite itself was not distinguished.
- Why it looks wrong: repeating the request changes the historical return date and can change the late fee shown for that loan.

## Impact
- Ledger capabilities: `loan.return-date`, `loan.return`
- Blocks: future migration tickets implementing these capabilities (not yet filed)

## Options
1. Preserve exactly (repeated returns overwrite the date; tests pin this behavior)
2. Fix (the target does not overwrite the date; the divergence is recorded with this ticket as approval)
3. Other
