# Billing source-derived examples

These examples cover the billing job and Northgate adapter, which are outside the source's existing test reach. They are predictions from the source, not executed observations. Tier-B compilation below intentionally resolves only the calculator and line classes reached by tests; it does not compile or invoke the private vault integration.

| Capability | Input | Predicted behavior | Source |
|---|---|---|---|
| `billing.monthly-run` | `ana` has `$4.75` in late fees; a charge is approved with reference `R1` | The job computes `$8.14`, calls `vault.charge("ana", 8.14)`, then prints `ana charged 8.14 ref R1`. | `legacy-billing/src/main/java/billing/BillingJob.java:15-23` |
| `billing.monthly-run` | First member's card is declined and a later member remains in the map | `CardVault.charge` throws; `BillingJob.run` does not catch it, so iteration stops before the later member. | `legacy-billing/src/main/java/billing/BillingJob.java:15-23`; `legacy-billing/src/main/java/billing/CardVault.java:16-20` |
| `billing.card-vault` | Member `ana`, amount `$8.14`, gateway approves with reference `R1` | The adapter submits 814 cents in USD and returns `R1`. | `legacy-billing/src/main/java/billing/CardVault.java:16-22` |
| `billing.card-vault` | Gateway declines member `ana` with reason `expired` | The adapter throws `IllegalStateException` with message `card declined for ana: expired`. | `legacy-billing/src/main/java/billing/CardVault.java:18-20` |
| `billing.job-startup` | `NORTHGATE_MERCHANT` and `NORTHGATE_KEY` are set | `main` connects with those values and submits hard-coded invoices for `ana` (`$4.75` late fee) and `ben` (no late fees), which total `$8.14` and `$3.15` respectively before charging. | `legacy-billing/src/main/java/billing/BillingJob.java:26-30`; `legacy-billing/src/main/java/billing/InvoiceCalculator.java:16-24` |

The last row was not executed: running this entry point with credentials could make real card charges. The Northgate client dependency is private, and none of these classes are reached by the source's own test class.
