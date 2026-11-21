# A declined card stops the remaining billing batch

## Question
A declined payment propagates out of `BillingJob.run` and prevents later members in the batch from being processed. Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/BillingJob.java:15-23`; `legacy-billing/src/main/java/billing/CardVault.java:16-20`
- Characterization: BL-02 Tier B seam test observed `IllegalStateException` on decline and confirmed that no later member output was produced; evidence is `.migration/characterization/billing/BillingCharacterization.java`.
- Why it looks wrong: One member's decline prevents subsequent independent member charges from being attempted.

## Impact
- Ledger capabilities: `billing.card-vault`, `billing.monthly-batch`
- Blocks: No work in BL-01; human ruling is needed before implementing batch failure handling.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
