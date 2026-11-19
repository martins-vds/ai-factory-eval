# Sub-cent card amounts fail exact conversion

## Question
`CardVault.charge` converts dollars to integer cents with `longValueExact`, so an amount containing a fractional cent throws `ArithmeticException` instead of being rounded; preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/CardVault.java:16-17`
- Characterization: Source-only trace, not executed in BL-01: charging `new BigDecimal("1.001")` reaches `longValueExact()` with 100.1 and throws before calling Northgate.
- Why it looks wrong: The method accepts arbitrary `BigDecimal` amounts but has no explicit precision validation or rounding policy for fractional cents.

## Impact
- Ledger capabilities: `billing.northgate-card-charge`
- Blocks: migration of card-amount precision behavior pending a human ruling

## Options
1. Preserve exactly (fractional-cent values throw; a test pins it)
2. Fix (define and apply an explicit precision or rounding policy; record the approved divergence)
3. Other
