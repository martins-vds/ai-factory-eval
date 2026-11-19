# Member billing cannot carry an invoice over

## Question
`BillingJob.run` calculates every invoice as a member invoice, so even an empty invoice totals $3.15 and is charged; should that monthly fee or member classification change?

## Evidence
- Source: `legacy-billing/src/main/java/billing/BillingJob.java:15-22` and `legacy-billing/src/main/java/billing/InvoiceCalculator.java:9-10,22-24`
- Characterization: `.migration/characterization/billing/observations.md`, case `test_empty_member_invoice_is_charged`; an empty invoice produces `$3.15` and calls the vault for `315` USD cents.
- Why it looks wrong: `BillingJob.run` has a carried-over branch for totals below `$1.00`, but its unconditional member fee makes that branch unreachable for valid nonnegative invoice lines.

## Impact
- Ledger capabilities: `billing.monthly-run`, `billing.charge-threshold`
- Blocks: any target implementation of member billing and carry-over handling until the policy is decided; characterization may record the behavior.

## Options
1. Preserve exactly (the target also charges empty member invoices and retains the unreachable carry-over branch)
2. Fix (change member classification or monthly-fee policy; record the approved divergence in the ledger)
3. Other
