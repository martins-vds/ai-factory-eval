# Sub-dollar carry-over is only reported

## Question
Should sub-dollar invoice totals be considered carried over when `BillingJob.run` only prints a carry-over message and stores no carry-over state in this source? Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/InvoiceCalculator.java:27-30`; `legacy-billing/src/main/java/billing/BillingJob.java:15-23`
- Characterization: `.migration/characterization/billing/observations.md` records that `chargeable(0.99)` is false, while `BillingJob.run` charges a member with an empty fee list at $3.15. Since valid `InvoiceLine` amounts are nonnegative and the job always includes the $3.00 member fee, the job's carry-over branch is unreachable for valid invoice input.
- Why it looks wrong: `chargeable` documents that a sub-dollar amount carries over to next month, but `BillingJob.run` only prints a carry-over message and stores no state; moreover, valid job inputs cannot produce the sub-dollar total that would enter that branch.

## Impact
- Ledger capabilities: `billing.charge-threshold`, `billing.job-processing`
- Blocks: Member-billing implementation ticket(s), to be identified by the coordinator.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
