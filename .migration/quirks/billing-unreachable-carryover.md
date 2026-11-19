# The monthly billing job cannot carry over a valid member invoice

## Question
`BillingJob.run` charges every valid member invoice instead of carrying over totals below $1.00 because the monthly member fee alone makes the total $3.15. Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/InvoiceCalculator.java:9-11,22-30`; `legacy-billing/src/main/java/billing/InvoiceLine.java:5-11`; `legacy-billing/src/main/java/billing/BillingJob.java:15-21`
- Characterization: Source review predicts an empty fee list for a member produces `$3.15`, which is chargeable; negative fees are rejected. The tier-B suite will record the seam observation.
- Why it looks wrong: `BillingJob.run` includes a carried-over branch, but no valid list of non-negative fee lines can reach it while the monthly fee is always included.

## Impact
- Ledger capabilities: `billing.invoice-calculation`, `billing.monthly-run`
- Blocks: Billing implementation tickets that choose how to handle the carried-over branch.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
