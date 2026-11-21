# Payment interruption is converted to a gateway error

## Question
When the gateway call is interrupted, the handler returns a 502 response without restoring the thread's interrupt flag; preserve, fix, or something else?

## Evidence
- Source: `legacy/src/main/java/lib/FinePayments.java:34-40`
- Characterization: Source-only inference: an `InterruptedException` follows the same response path as an `IOException` and leaves the interrupt flag cleared; no runtime trace was recorded in SY-04.
- Why it looks wrong: The cancellation signal can be lost to the caller or runtime.

## Impact
- Ledger capabilities: `payments.charge`
- Blocks: Implementation decision for `payments.charge` (ticket link pending orchestration).

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
