# A null invoice line amount fails with NullPointerException

## Question
Should constructing an invoice line with a null amount continue to fail with NullPointerException, or should the input be rejected explicitly? Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/InvoiceLine.java:6-10`
- Characterization: Source trace: `new InvoiceLine("late", null)` calls `amount.signum()` and throws NullPointerException. A tier-B characterization test is being added for this path.
- Why it looks wrong: Negative amounts are explicitly rejected with IllegalArgumentException, but a missing amount fails incidentally with a different exception.

## Impact
- Ledger capabilities: `billing.invoice-line`
- Blocks: Future ticket implementing invoice-line validation (not yet planned)

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
