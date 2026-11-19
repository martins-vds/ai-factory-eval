# A declined card stops the billing batch

## Question
When a member's charge is declined, `CardVault.charge` throws and `BillingJob.run` exits before processing later entries; should one decline stop the entire batch?

## Evidence
- Source: `legacy-billing/src/main/java/billing/CardVault.java:18-20` and `legacy-billing/src/main/java/billing/BillingJob.java:15-23`
- Characterization: `.migration/characterization/billing/observations.md`, case `test_declined_charge_stops_batch`; the first entry's decline throws and only that member is sent to the vault.
- Why it looks wrong: one member's declined payment can prevent unrelated members later in the iteration from being billed or reported.

## Impact
- Ledger capabilities: `billing.card-vault`, `billing.monthly-run`
- Blocks: any target implementation of batch failure handling until the policy is decided; characterization may record the behavior.

## Options
1. Preserve exactly (target stops the batch on the first decline; a test pins it)
2. Fix (target records the decline and continues; the divergence is recorded in the ledger with this ticket as approval)
3. Other
