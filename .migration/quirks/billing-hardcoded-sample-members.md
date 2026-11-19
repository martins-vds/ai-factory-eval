# Billing entrypoint uses hardcoded sample members

## Question
Should `BillingJob.main` charge the hardcoded `ana` and `ben` records on every invocation, rather than load the members and amounts for the monthly run? Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/BillingJob.java:26-30`
- Characterization: `.migration/characterization/billing/observations.md` records a separate-JVM run with test environment credentials and an ignored command-line argument. It still charges the fixed Ana $4.75 and Ben empty-fee sample, producing $8.14 and $3.15 respectively.
- Why it looks wrong: The executable entrypoint ignores its arguments and always invokes the billing job with a fixed map containing `ana`'s $4.75 fee and `ben`'s empty fee list, rather than reading a monthly member-billing input.

The observed member order is covered separately by `.migration/quirks/billing-member-map-order.md`.

## Impact
- Ledger capabilities: `billing.job-entrypoint`, `billing.job-processing`
- Blocks: Member-billing implementation ticket(s), to be identified by the coordinator.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
