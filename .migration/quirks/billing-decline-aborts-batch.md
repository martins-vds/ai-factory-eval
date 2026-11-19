# A declined card aborts the remaining monthly billing run

## Question
When a member's card is declined, should the monthly billing run terminate, or continue processing the remaining members? Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/CardVault.java:16-20`; `legacy-billing/src/main/java/billing/BillingJob.java:15-23`
- Characterization: Source trace: when `vault.charge` rejects a member, `CardVault.charge` throws `IllegalStateException`; `BillingJob.run` does not catch it in the loop, so later members are not processed. This path is not yet executed.
- Why it looks wrong: A single declined member can prevent unrelated members later in the batch from being billed or reported.

## Impact
- Ledger capabilities: `billing.monthly-run`, `billing.card-vault`
- Blocks: Future ticket implementing the affected billing capabilities (not yet planned)

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
