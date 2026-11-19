# BillingJob.main charges hard-coded sample members

## Question
Should running the billing job's `main` method use its hard-coded Ana and Ben sample invoices with live Northgate credentials, or should it avoid charging sample data? Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/BillingJob.java:26-30`; `legacy-billing/src/main/java/billing/CardVault.java:12-19`
- Characterization: Source trace: `main` reads `NORTHGATE_MERCHANT` and `NORTHGATE_KEY`, constructs a live `CardVault`, then invokes `run` on hard-coded invoices for `ana` and `ben`. Not executed because it could issue real card charges.
- Why it looks wrong: The command-line entry point describes a monthly billing job but its input is sample data and its configured gateway can perform real charges.

## Impact
- Ledger capabilities: `billing.job-startup`, `billing.card-vault`
- Blocks: Future ticket implementing the billing entry point (not yet planned)

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
