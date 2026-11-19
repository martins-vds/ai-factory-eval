# Sub-dollar carry-over is only reported

## Question
Should sub-dollar invoice totals be considered carried over when `BillingJob.run` only prints a carry-over message and stores no carry-over state in this source? Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/InvoiceCalculator.java:27-30`; `legacy-billing/src/main/java/billing/BillingJob.java:15-23`
- Characterization: Not run; BL-01 inventories source behavior only.
- Why it looks wrong: `chargeable` documents that a sub-dollar amount carries over to next month, but `BillingJob.run` only prints that it was carried over; no persistence or returned carry-over value is present in the source.

## Impact
- Ledger capabilities: `billing.charge-threshold`, `billing.job-processing`
- Blocks: Member-billing implementation ticket(s), to be identified by the coordinator.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
