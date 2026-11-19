# Member billing characterization

Tier B, at the billing source seams. The source graph intentionally does not cover `legacy-billing/` (BL-01, issue #1548); source files and the one existing test class were inspected directly. The original `InvoiceCalculatorTest` has six tests. The isolated suite compiled the four original production classes and ran those six tests plus 16 characterization tests: 22 passed, 0 failed.

Run: `.migration/evidence/runs/BL-02.md` (`mvn -q -f .migration/characterization/billing/pom.xml test`).

The three `com.northgate.vault` classes under `src/main/java` are local API stand-ins. They capture constructor credentials and charge arguments and return a configured result; they perform no network access and do not characterize Northgate's implementation or service.

| Capability | Test | Predicted from source | Observed |
|---|---|---|---|
| Invoice calculation | `InvoiceCalculatorTest.memberWithOneLateFee` | Member fee $3.00 plus $4.75 late fee and rounded tax gives $8.14. | $8.14 |
| Invoice calculation | `InvoiceCalculatorTest.lateFeesAreCappedButTheMonthlyFeeIsNot` | Late fees cap at $25.00; monthly fee is added outside the cap; total is $29.40. | $29.40 |
| Invoice calculation | `InvoiceCalculatorTest.nonMemberPaysOnlyFees` | $2.00 fee plus 5% tax gives $2.10 for a non-member. | $2.10 |
| Invoice calculation | `InvoiceCalculatorTest.taxRoundsHalfUpOnce` | $0.50 fee plus half-up tax gives $0.53. | $0.53 |
| Invoice calculation | `InvoiceCalculatorTest.underADollarCarriesOver` | $0.99 is not chargeable; $1.00 is chargeable. | False at $0.99; true at $1.00. |
| Invoice line | `InvoiceCalculatorTest.negativeChargesAreRejected` | A negative amount is rejected with `IllegalArgumentException`. | `IllegalArgumentException`. |
| Invoice calculation | `BillingCharacterizationTest.calculatorTotalsMemberAndNonMemberInvoices` | Member $4.75 fee totals $8.14; non-member $2.00 fee totals $2.10. | $8.14 and $2.10. |
| Invoice calculation | `BillingCharacterizationTest.calculatorHandlesEmptyFeesAndCapBoundary` | Empty member/non-member lists total $3.15/$0.00; $25.00 and $25.01 non-member fee totals both cap at $26.25. | $3.15, $0.00, $26.25 and $26.25. |
| Invoice calculation | `BillingCharacterizationTest.calculatorRoundsTaxHalfUpAndUsesOneDollarThreshold` | $0.50 totals $0.53; only totals at least $1.00 are chargeable. | $0.53; false at $0.99 and true at $1.00. |
| Invoice calculation | `BillingCharacterizationTest.calculatorFailsForNullFeeListAndNullFeeLine` | A null fee list or null line is dereferenced without explicit validation. | Both inputs throw `NullPointerException`. |
| Invoice line | `BillingCharacterizationTest.invoiceLineRejectsNegativeAmountWithDescription` | A negative amount throws with its description in the message. | `IllegalArgumentException: negative charge: late: L3`. |
| Invoice line | `BillingCharacterizationTest.invoiceLineAcceptsZeroAndExposesRecordComponents` | Zero is accepted; description and amount are exposed unchanged. | Description `late`; amount `0.00`. |
| Invoice line | `BillingCharacterizationTest.invoiceLineFailsForNullAmountWithNullPointerException` | Null reaches `amount.signum()` without validation. | `NullPointerException`. |
| Monthly run | `BillingCharacterizationTest.billingJobChargesEachMemberInMapOrder` | Members are processed in map order, with monthly fee, output line, and charge per member. | Ana charged $8.14 then Ben $3.15; 814 and 315 USD cents were submitted in that order. |
| Monthly run | `BillingCharacterizationTest.billingJobDoesNothingForAnEmptyMap` | An empty map produces no output or charge. | No output or charge. |
| Monthly run | `BillingCharacterizationTest.billingJobPropagatesDeclineAndSkipsLaterMembers` | A declined first charge propagates and prevents the next map entry. | `IllegalStateException` for Ana; Ben was not charged. |
| Monthly run | `BillingCharacterizationTest.billingJobRejectsNullMemberMap` | A null map is dereferenced without explicit validation. | `NullPointerException`; no charge. |
| Northgate adapter | `BillingCharacterizationTest.cardVaultConnectsAndSendsExactUsdCents` | Credentials are passed at connect; $8.14 is sent as 814 USD cents; approved reference is returned. | Stand-in observed both credentials and `(member-9, 814, USD)`; returned `test-reference`. |
| Northgate adapter | `BillingCharacterizationTest.cardVaultThrowsOnDecline` | A decline throws with member ID and reason after submitting exact cents. | `IllegalStateException: card declined for member-9: expired`; 814 USD cents submitted. |
| Northgate adapter | `BillingCharacterizationTest.cardVaultRejectsAmountsThatCannotBeConvertedToExactCents` | A fractional-cent amount fails exact integer conversion before a charge. | $1.001 throws `ArithmeticException`; no charge submitted. |
| Build and run | `BillingCharacterizationTest.buildTargetsJava17AndDeclaresThePrivateVaultDependency` | POM declares Java 17 and the Northgate private repository/artifact. | All declarations were present. |
| Build and run | `BillingCharacterizationTest.launcherPackagesBeforeUsingTheTargetDependencyWildcard` | Launcher packages first, then uses `target/classes:target/dependency/*`. | Both commands/path were present. |

No behavior differed from the source-based predictions. The empty-list member case also confirms the `BillingJob` carry-over branch is unreachable for valid non-negative fee lines: its $3.15 minimum is chargeable. The real private Maven build and Northgate service were not run.
