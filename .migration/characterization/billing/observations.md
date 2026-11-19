# Member-billing characterization

Source: `legacy-billing/` at target commit `367ae2d860334d239d1ebc479cfa232550defd78`. This source has no code graph or risk map (BL-01 operator decision); the source and its tests are the authority.

## Tier-B method

The harness compiles the source's billing classes and its own JUnit test class with a local stand-in for the three `com.northgate.vault` types (`VaultClient`, `VaultCredentials`, `ChargeResult`). The stand-in records charge arguments and supplies controlled approvals/declines. The original source is not modified and the full source build is not run because its Northgate dependency is private. Command: `mvn -B -f .migration/characterization/billing/pom.xml test`.

## Predicted versus observed

Predictions below are from the cited source rules; observations are from the source tests and the tier-B seam suite. Each JUnit test method is one case.

| Test case | Predicted from source | Observed |
|---|---|---|
| `InvoiceCalculatorTest.memberWithOneLateFee` | Member fee $3.00 plus $4.75 late fee and tax totals $8.14. | $8.14; match. |
| `InvoiceCalculatorTest.lateFeesAreCappedButTheMonthlyFeeIsNot` | Combined $32.50 fees cap at $25.00; with membership fee and tax the total is $29.40. | $29.40; match. |
| `InvoiceCalculatorTest.nonMemberPaysOnlyFees` | $2.00 fee plus tax totals $2.10 without membership fee. | $2.10; match. |
| `InvoiceCalculatorTest.taxRoundsHalfUpOnce` | $0.50 fee has $0.03 half-up tax and totals $0.53. | $0.53; match. |
| `InvoiceCalculatorTest.underADollarCarriesOver` | $0.99 is not chargeable; $1.00 is chargeable. | `false`, `true`; match. |
| `InvoiceCalculatorTest.negativeChargesAreRejected` | A negative line amount throws `IllegalArgumentException`. | Exception thrown; match. |
| `BillingCharacterizationTest.invoiceTotalsCoverEmptyFeesCapAndTax` | Empty member/nonmember totals are $3.15/$0.00; capped member fees total $29.40; $0.50 nonmember fee totals $0.53. | All four totals matched. |
| `BillingCharacterizationTest.invoiceLinesRejectNegativeAndAllowZero` | Zero is accepted; -$0.01 throws `IllegalArgumentException` with `negative charge: late`. | Both outcomes and message matched. |
| `BillingCharacterizationTest.nullInvoiceLineAmountThrowsNullPointerException` | Null reaches `amount.signum()` and throws `NullPointerException`. | `NullPointerException`; match; recorded as a quirk for human review. |
| `BillingCharacterizationTest.chargeThresholdIsInclusiveAtOneDollar` | $0.00, $0.99 and -$0.01 are not chargeable; $1.00 is chargeable. | `false`, `false`, `false`, `true`; match. |
| `BillingCharacterizationTest.cardVaultSubmitsExactUsdCentsAndReturnsReference` | $12.34 is submitted as 1234 USD cents; zero is submitted as 0 USD cents; the approval reference is returned. | Recorded requests and references matched. |
| `BillingCharacterizationTest.cardVaultDeclinesAndRejectsFractionalCents` | A decline throws `IllegalStateException` with member and reason; a $1.001 amount fails exact-cent conversion. | Both exceptions and decline text matched. |
| `BillingCharacterizationTest.billingJobChargesEachMemberAndCarriesEmptyMemberFeesIntoMembershipTotal` | Ana's $4.75 fee is charged as $8.14; Ben's empty fee list produces a $3.15 member total and is charged, not carried over. | Output and 814/315-cent USD requests matched. |
| `BillingCharacterizationTest.billingJobIsSilentForNoMembersAndPropagatesDeclines` | Empty input produces no output or charge; a card decline propagates. | Both outcomes matched. |
| `BillingCharacterizationTest.billingJobRejectsNullInvoiceList` | A null list reaches `lateFees.stream()` and throws `NullPointerException`. | `NullPointerException`; match. |
| `BillingCharacterizationTest.entryPointReadsEnvironmentAndUsesFixedMembersRegardlessOfArguments` | The environment values construct the vault; ignored arguments do not change the fixed Ana/Ben sample or their totals. Initial order prediction was Ana then Ben from the source listing. | Credential checks and both outputs/totals matched, but a separate-JVM run emitted Ben before Ana. The test now asserts membership/results without imposing order; order difference recorded as a quirk. |

Final run: 16 test methods, 16 passing, 0 failing. Across the 16 method-level predictions, 15 matched and one differed only on the entrypoint's member iteration order.

## Notes for target characterization

- Valid invoice lines have nonnegative amounts. With `member=true`, `BillingJob.run` therefore computes a minimum of $3.15, so its under-$1 carry-over branch cannot be reached through valid invoice input; the direct `chargeable` method does return false below $1.
- The entrypoint uses `Map.of` and `run` iterates the supplied map. Do not treat sample member processing order as guaranteed.
- The Northgate stand-in verifies the billing adapter's arguments and response handling; it does not characterize the private vendor client's internal behavior.
