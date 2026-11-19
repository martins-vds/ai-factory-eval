# Null invoice amounts fail with an incidental exception

## Question
What should happen when an invoice line has a null amount? Preserve the current null failure, reject it explicitly, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/InvoiceLine.java:6-9`
- Characterization: `new InvoiceLine("late", null)` reaches `amount.signum()` and throws `NullPointerException`.
- Why it looks wrong: the constructor explicitly rejects negative amounts but has no corresponding null validation, so callers receive an incidental dereference failure for a missing amount.

## Impact
- Ledger capabilities: `billing.invoice-line`
- Blocks: a human ruling before implementing the null-amount behavior in the target.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
