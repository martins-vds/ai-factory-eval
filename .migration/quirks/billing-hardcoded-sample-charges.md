# Billing entry point charges hard-coded sample members

## Question
`BillingJob.main` always runs the hard-coded ana and ben sample invoices using the configured Northgate credentials. Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/BillingJob.java:26-30`; `legacy-billing/run.sh:2-6`
- Characterization: BL-02 Tier B seam test ran `BillingJob.main` with stand-in Northgate and observed hard-coded `ana` and `ben` charges using `NORTHGATE_MERCHANT` and `NORTHGATE_KEY`; evidence is `.migration/characterization/billing/BillingCharacterization.java`.
- Why it looks wrong: Running the documented job can submit charges for fixed sample member IDs instead of loading the month's actual billing data.

## Impact
- Ledger capabilities: `billing.job-entrypoint`
- Blocks: No work in BL-01; human ruling is needed before implementing the entry point.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
