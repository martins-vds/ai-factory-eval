# Member billing characterization (Tier B)

- Source revision: `1bacc561` (the billing sources were unchanged at this branch revision).
- Suite: `python -m unittest discover -s .migration/characterization/billing -p 'test_*.py' -v`
- Gate: `.migration/evidence/runs/BL-02.md`, final `characterize-final` run, 28 tests passed.
- All 28 predicted results matched the observed result.

The suite compiles only `InvoiceLine`, `InvoiceCalculator`, `CardVault`, and `BillingJob` from
`legacy-billing/`. The `com.northgate.vault` classes are compile-only stand-ins that record calls and
return controlled results; no network request is made. The launcher case runs the real `run.sh` with
fake `mvn` and `java` executables to capture its command sequence. It does not resolve the private
Northgate dependency or establish whether a real package launch succeeds.

The six legacy JUnit methods in `legacy-billing/src/test/java/billing/InvoiceCalculatorTest.java`
were inventoried and their assertions are replayed by this suite. The private dependency prevents
running the source Maven test lifecycle; the focused javac harness compiles and executes the reached
source units instead.

| Test | Predicted from source | Observed |
|---|---|---|
| `test_invoice_line_accepts_zero` | `0.00` accepted | `0.00` accepted |
| `test_invoice_line_rejects_negative_amount` | `IllegalArgumentException:negative charge: late` | `IllegalArgumentException:negative charge: late` |
| `test_invoice_line_null_amount_fails` | `NullPointerException` | `NullPointerException` |
| `test_member_invoice_total` | member fee `$3.00` plus `$4.75` late fee and tax totals `8.14` | `8.14` |
| `test_late_fees_are_capped_before_monthly_fee_and_tax` | capped fees `$25.00`, member fee `$3.00`, tax totals `29.40` | `29.40` |
| `test_nonmember_invoice_total` | `$2.00` plus tax totals `2.10` | `2.10` |
| `test_tax_rounds_half_up_once` | `$0.50` plus half-up tax totals `0.53` | `0.53` |
| `test_empty_member_invoice_includes_monthly_fee_and_tax` | empty member invoice totals `3.15` | `3.15` |
| `test_empty_nonmember_invoice_is_zero` | empty nonmember invoice totals `0.00` | `0.00` |
| `test_null_fee_list_fails` | `NullPointerException` | `NullPointerException` |
| `test_null_fee_line_fails` | `NullPointerException` | `NullPointerException` |
| `test_amount_below_one_dollar_is_not_chargeable` | `0.99` is not chargeable | `false` |
| `test_amount_at_one_dollar_is_chargeable` | `1.00` is chargeable | `true` |
| `test_null_total_fails` | `NullPointerException` | `NullPointerException` |
| `test_empty_batch_has_no_output_or_charges` | no output and no vault call | no output and no vault call |
| `test_empty_member_invoice_is_charged` | empty member invoice totals `3.15` and charges `315` USD cents | `member charged 3.15 ref ref-member`; `member:315:USD` |
| `test_batch_charges_each_member_and_reports_references` | ordered members are charged and reported | `first charged 8.14 ref ref-first`; `second charged 3.15 ref ref-second`; calls `814` and `315` USD cents |
| `test_declined_charge_stops_batch` | first decline throws and prevents the second member call | `IllegalStateException:card declined for first: insufficient funds`; only `first:814:USD` called |
| `test_null_batch_fails` | `NullPointerException` | `NullPointerException` |
| `test_null_member_fees_fail` | `NullPointerException` | `NullPointerException` |
| `test_vault_converts_approved_charge_to_cents_and_returns_reference` | `$8.14` calls Northgate with `814` USD cents and returns the approved reference | `ref-member`; credential `merchant:key`; call `member:814:USD` |
| `test_vault_passes_zero_amount_as_zero_cents` | zero converts to `0` cents | `member:0:USD` |
| `test_vault_passes_negative_amount_as_negative_cents` | `-$1.00` converts to `-100` cents | `member:-100:USD` |
| `test_vault_rejects_fractional_cent_without_calling_provider` | `$1.001` fails exact integer conversion before provider call | `ArithmeticException:Rounding necessary`; no call |
| `test_vault_null_amount_fails_without_calling_provider` | null amount fails before provider call | `NullPointerException`; no call |
| `test_vault_decline_throws_provider_reason` | declined `$4.20` throws with member and provider reason | `IllegalStateException:card declined for member: insufficient funds`; call `member:420:USD` |
| `test_entrypoint_reads_credentials_and_bills_fixed_members` | environment credentials are passed to the vault; Ana and Ben are billed using the fixed examples | credential `characterization-merchant:characterization-key`; Ana `8.14` / `814` cents and Ben `3.15` / `315` cents |
| `test_launcher_runs_maven_then_java_with_target_dependency_classpath` | run Maven package, then launch with `target/classes:target/dependency/*` | `mvn -q -B package`, then `java -cp target/classes:target/dependency/* billing.BillingJob` |

Legacy test inventory and matching characterization cases:

| Legacy test | Asserted behavior | Suite cases |
|---|---|---|
| `memberWithOneLateFee` | member total is `8.14` | `test_member_invoice_total` |
| `lateFeesAreCappedButTheMonthlyFeeIsNot` | capped late fees plus monthly fee total `29.40` | `test_late_fees_are_capped_before_monthly_fee_and_tax` |
| `nonMemberPaysOnlyFees` | nonmember total is `2.10` | `test_nonmember_invoice_total` |
| `taxRoundsHalfUpOnce` | half-up tax total is `0.53` | `test_tax_rounds_half_up_once` |
| `underADollarCarriesOver` | `0.99` is below threshold and `1.00` meets it | `test_amount_below_one_dollar_is_not_chargeable`, `test_amount_at_one_dollar_is_chargeable` |
| `negativeChargesAreRejected` | negative invoice lines throw `IllegalArgumentException` | `test_invoice_line_rejects_negative_amount` |

The first harness attempt exposed unstable JDK exception-message expectations and incorrect quoting in
the fake launcher. Those harness issues were corrected; the final run passed all 28 cases.
