# Null billing collections fail through incidental dereferences

## Question
`InvoiceCalculator.total` and `BillingJob.run` throw `NullPointerException` for null collections instead of explicit validation; preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/InvoiceCalculator.java:15-16`; `legacy-billing/src/main/java/billing/BillingJob.java:14-15`
- Characterization: `BillingCharacterizationTest.calculatorFailsForNullFeeListAndNullFeeLine` observed `NullPointerException` for a null fee list and a null line; `BillingCharacterizationTest.billingJobRejectsNullMemberMap` observed `NullPointerException` for a null member map.
- Why it looks wrong: Callers receive an incidental null dereference rather than a deliberate input-validation result.

## Impact
- Ledger capabilities: `billing.invoice-calculation`, `billing.monthly-run`
- Blocks: Billing implementation tickets that choose how null collections should be handled.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
