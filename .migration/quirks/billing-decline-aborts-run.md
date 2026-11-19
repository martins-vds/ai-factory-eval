# A declined card aborts the remaining monthly billing run

## Question
When a member's Northgate charge is declined, `BillingJob.run` propagates the exception and skips every later member in the map. Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/CardVault.java:16-21`; `legacy-billing/src/main/java/billing/BillingJob.java:15-23`
- Characterization: Source-derived behavior: if a charge in the loop is declined, `CardVault.charge` throws `IllegalStateException`; `BillingJob.run` has no catch, so the call exits before reaching later entries. The analyst has not run the private-vault integration.
- Why it looks wrong: One card's decline can leave a monthly run only partially processed, with no per-member continuation or batch-level recovery.

## Impact
- Ledger capabilities: `billing.monthly-run`, `billing.northgate-card-vault`
- Blocks: No implementation ticket is in this analyst ticket's scope; the behavior needs a human decision before it is implemented.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
