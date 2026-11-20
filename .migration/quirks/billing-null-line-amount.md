# Null invoice line amount fails with NullPointerException

## Question
`InvoiceLine` dereferences a null amount while checking for negative charges, producing `NullPointerException` rather than an explicit validation error. Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/InvoiceLine.java:6-10`
- Characterization: Not performed in analyst ticket BL-01; constructor behavior follows directly from the null dereference in `amount.signum()`.
- Why it looks wrong: The constructor explicitly validates invalid negative amounts but leaves null amounts to fail incidentally.

## Impact
- Ledger capabilities: `billing.invoice-line`
- Blocks: No work in BL-01; human ruling is needed before changing null-amount handling.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
