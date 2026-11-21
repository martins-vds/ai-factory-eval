# Payment gateway loan id is not URI-encoded

## Question
The payment request appends the loan id directly to the gateway query string rather than encoding it as one query value; preserve, fix, or something else?

## Evidence
- Source: `legacy/src/main/java/lib/FinePayments.java:33-37`
- Characterization: Source-only inference: an id containing URI-reserved characters may change how the gateway parses the request; no runtime trace was recorded in SY-04.
- Why it looks wrong: A loan id should be transmitted as a single query value, but raw concatenation leaves URI interpretation dependent on its characters.

## Impact
- Ledger capabilities: `payments.charge`
- Blocks: Implementation decision for `payments.charge` (ticket link pending orchestration).

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
