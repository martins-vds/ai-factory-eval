# A declined card aborts the remaining monthly billing run

## Question
When a member's card is declined, `CardVault.charge` throws and `BillingJob.run` does not catch it, so processing stops before later members are attempted. Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/CardVault.java:16-20`; `legacy-billing/src/main/java/billing/BillingJob.java:15-23`
- Characterization: Source-only inspection (tier B); the exception is thrown from the per-member loop and propagates out of `run`. No runtime characterization was performed.
- Why it looks wrong: One member's declined payment prevents the monthly run from attempting charges for all subsequent members.

## Impact
- Ledger capabilities: `billing.monthly-run`, `billing.northgate-card-charge`
- Blocks: Future billing implementation ticket(s) must depend on the human decision; BL-01 inventory is not blocked.

## Options
1. Preserve exactly (the target stops the run on the first declined card)
2. Fix (the target records the decline and continues with subsequent members)
3. Other
