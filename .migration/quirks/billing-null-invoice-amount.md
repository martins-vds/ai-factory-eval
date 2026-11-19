# Null invoice-line amounts throw an implicit exception

## Question
Should constructing an `InvoiceLine` with a null amount throw `NullPointerException`, or should it use an explicit validation error? Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/InvoiceLine.java:5-11`
- Characterization: `.migration/characterization/billing/observations.md` records that `new InvoiceLine("late", null)` throws `NullPointerException`.
- Why it looks wrong: Negative amounts are explicitly rejected with `IllegalArgumentException`, but a null amount is dereferenced by `amount.signum()` before any explicit validation.

## Impact
- Ledger capabilities: `billing.invoice-line-validation`
- Blocks: Member-billing implementation ticket(s), to be identified by the coordinator.

## Options
1. Preserve exactly (the target reproduces the exception; a test pins it)
2. Fix (the target uses explicit validation; the divergence is recorded in the ledger with this ticket as approval)
3. Other
