# A null invoice-line amount fails with an unhelpful null dereference

## Question
Constructing an `InvoiceLine` with a null amount throws `NullPointerException` at `amount.signum()` rather than a deliberate validation error. Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/InvoiceLine.java:6-10`
- Characterization: Source-derived behavior: `new InvoiceLine("late", null)` evaluates `amount.signum()` and throws `NullPointerException`; the existing source test covers negative values but not null.
- Why it looks wrong: The record explicitly validates negative monetary amounts, but does not define null handling, so callers receive an incidental exception for an invalid amount.

## Impact
- Ledger capabilities: `billing.invoice-line`
- Blocks: No implementation ticket is in this analyst ticket's scope; the behavior needs a human decision before it is implemented.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
