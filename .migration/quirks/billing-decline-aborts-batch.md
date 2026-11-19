# A declined card aborts the remaining billing batch

## Question
When a member's card is declined, `BillingJob.run` lets the exception escape and stops processing later map entries; preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/BillingJob.java:15-23`; `legacy-billing/src/main/java/billing/CardVault.java:16-20`
- Characterization: Source-only trace, not executed in BL-01: if `vault.charge` throws for an entry, the loop exits before subsequent entries are processed.
- Why it looks wrong: One member's declined card prevents unrelated members later in the batch from being billed, and map iteration order can affect which entries are reached.

## Impact
- Ledger capabilities: `billing.monthly-job`, `billing.northgate-card-charge`
- Blocks: migration of per-member failure handling pending a human ruling

## Options
1. Preserve exactly (the first decline aborts the batch; a test pins it)
2. Fix (record the failure and continue with other members; record the approved divergence)
3. Other
