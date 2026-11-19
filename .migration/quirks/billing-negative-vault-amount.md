# Card vault accepts negative amounts

## Question
`CardVault.charge` forwards a negative exact-cent amount to Northgate; should it reject negative amounts before calling the provider?

## Evidence
- Source: `legacy-billing/src/main/java/billing/CardVault.java:16-17`
- Characterization: `.migration/characterization/billing/observations.md`, case `test_vault_passes_negative_amount_as_negative_cents`; `-1.00` is submitted as `-100` USD cents.
- Why it looks wrong: invoice lines reject negative amounts, but the public vault method does not, allowing direct callers to submit a negative charge.

## Impact
- Ledger capabilities: `billing.card-vault`
- Blocks: any target implementation of card amount validation until the policy is decided; characterization may record the behavior.

## Options
1. Preserve exactly (the target forwards negative cents to the provider)
2. Fix (reject negative amounts and record the approved divergence in the ledger)
3. Other
