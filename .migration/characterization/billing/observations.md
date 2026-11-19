# Member billing characterization

## Source and tier

The source is `legacy-billing/` at the branch's initial checkout commit `72e16a907f419444764c95f5a862c1b7317faf08`; it is not covered by `.migration/source.lock` and was left untouched. The source declares Java 17, Maven, UTF-8, JUnit 4.13.2, and the private `com.northgate.vault:vault-client:4.2.1` dependency.

Tier B is available for the source code reached by `InvoiceCalculatorTest`: the calculator and invoice-line classes compile and execute with public JUnit and Hamcrest artifacts. The full application path is not compiled because the source tests do not reach `BillingJob` or `CardVault`, and the latter imports the private vault API.

## Tier-B run

The public test artifacts were fetched with:

```sh
mvn -B org.apache.maven.plugins:maven-dependency-plugin:3.6.1:get -Dartifact=junit:junit:4.13.2 -Dtransitive=true
```

The test command was run through `afs-run` as ticket `BL-02`:

```sh
bash -lc 'set -eu; classes_dir=/tmp/afs-billing-bl02/classes; mkdir -p "$classes_dir"; junit="$HOME/.m2/repository/junit/junit/4.13.2/junit-4.13.2.jar"; hamcrest="$HOME/.m2/repository/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar"; javac -sourcepath legacy-billing/src/main/java -implicit:class -cp "$junit:$hamcrest" -d "$classes_dir" legacy-billing/src/test/java/billing/InvoiceCalculatorTest.java .migration/characterization/billing/InvoiceCalculatorCharacterizationTest.java; java -cp "$classes_dir:$junit:$hamcrest" org.junit.runner.JUnitCore billing.InvoiceCalculatorTest billing.InvoiceCalculatorCharacterizationTest'
```

Observed result: `OK (12 tests)`. The compiled source classes were only `InvoiceCalculator` and `InvoiceLine`; no vendor stand-ins or external payment calls were used.

## Predicted versus observed

All 12 test methods matched their predictions. The original source tests and the added seam tests observe:

| Input | Predicted behavior | Observed |
|---|---|---|
| Member late fee `$4.75` | `$8.14` total | `$8.14` |
| Member late fees `$20.00` and `$12.50` | Cap late fees at `$25.00`, add `$3.00` membership fee and tax, return `$29.40` | `$29.40` |
| Non-member late fee `$2.00` | `$2.10` total | `$2.10` |
| Non-member late fee `$0.50` | Tax rounds half-up once; `$0.53` total | `$0.53` |
| Totals `$0.99` and `$1.00` | `$0.99` not chargeable; `$1.00` chargeable | `false`, `true` |
| Negative line amount `-$1.00` | Throw `IllegalArgumentException` | Expected exception |
| Empty member invoice | Monthly fee plus tax gives `$3.15` | `$3.15` |
| Empty non-member invoice | `$0.00` total | `$0.00` |
| Non-member invoice with a zero-valued line | Accept the line; return `$0.00` | `$0.00` |
| Member invoice with exactly `$25.00` late fees | Apply the cap at the boundary; return `$29.40` | `$29.40` |
| Totals `$0.00`, `$0.99`, and `$1.00` | First two not chargeable; `$1.00` chargeable | `false`, `false`, `true` |
| Invoice line with null amount | `amount.signum()` throws `NullPointerException` | Expected exception |

The source-derived examples for monthly orchestration, gateway behavior, and startup are recorded separately in `source-derived.md`; they are not described as executed observations.

## Limitations

The billing job and gateway adapter were not run because their code is not reached by the source's test class; running the entry point with its hard-coded sample data and credentials could charge real cards. Their examples are tier-C source-derived predictions pending a safe seam and human decisions on the quirk drafts.
