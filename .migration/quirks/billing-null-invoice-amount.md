# Null invoice amounts fail with an implicit NullPointerException

## Question
`InvoiceLine` calls `amount.signum()` without checking for null, so a null amount fails with `NullPointerException` rather than a deliberate validation error. Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/InvoiceLine.java:6-10`
- Characterization: Source-only inspection (tier B); invoking the record constructor with a null amount reaches `amount.signum()`. No runtime characterization was performed.
- Why it looks wrong: A missing amount is rejected incidentally rather than through an explicit invoice-line validation outcome.

## Impact
- Ledger capabilities: `billing.invoice-line`
- Blocks: Future billing implementation ticket(s) must depend on the human decision; BL-01 inventory is not blocked.

## Options
1. Preserve exactly (a null amount produces `NullPointerException`)
2. Fix (the target rejects it with explicit, documented validation)
3. Other
