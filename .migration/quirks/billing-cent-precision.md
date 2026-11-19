# Exact-cent conversion rejects fractional cents

## Question
`CardVault.charge` converts a decimal amount to integer cents with `longValueExact`, so amounts that are not an exact number of cents fail instead of being rounded; preserve, reject explicitly, or round?

## Evidence
- Source: `legacy-billing/src/main/java/billing/CardVault.java:16-17`
- Characterization: `.migration/characterization/billing/observations.md`, case `test_vault_rejects_fractional_cent_without_calling_provider`; `$1.001` throws `ArithmeticException:Rounding necessary` before a provider call.
- Why it looks wrong: the public charge method accepts `BigDecimal` without documenting a cents-only input requirement or translating this failure into a billing validation error.

## Impact
- Ledger capabilities: `billing.card-vault`
- Blocks: any target implementation of card amount conversion until the policy is decided; characterization may record the behavior.

## Options
1. Preserve exactly (target reproduces the exception; a test pins it)
2. Fix (target applies a defined rounding or validation policy; the divergence is recorded in the ledger with this ticket as approval)
3. Other
