# Billing entry point charges hard-coded sample members

## Question
`BillingJob.main` always runs the hard-coded ana and ben sample invoices using the configured Northgate credentials. Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/BillingJob.java:26-30`; `legacy-billing/run.sh:2-6`
- Characterization: Not performed in analyst ticket BL-01; the entry point calls the real `CardVault` with the sample batch.
- Why it looks wrong: Running the documented job can submit charges for fixed sample member IDs instead of loading the month's actual billing data.

## Impact
- Ledger capabilities: `billing.job-entrypoint`
- Blocks: No work in BL-01; human ruling is needed before implementing the entry point.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
