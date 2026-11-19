# The billing run script does not provision its runtime dependencies

## Question
`run.sh` invokes `mvn package` and then launches Java with `target/dependency/*`, but the POM does not configure dependency copying into that directory. Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/run.sh:3-6`; `legacy-billing/pom.xml:14-26`
- Characterization: Source-derived behavior: Maven packages the project, after which the script assumes runtime dependencies are available under `target/dependency`; the POM declares the Northgate client but does not configure that directory to be populated. The private Northgate repository prevents verifying the full build in this analyst task.
- Why it looks wrong: On a clean checkout the runtime classpath appears to omit the declared Northgate client and can fail when `BillingJob` loads `CardVault`.

## Impact
- Ledger capabilities: `billing.build-run`, `billing.northgate-card-vault`
- Blocks: No implementation ticket is in this analyst ticket's scope; the behavior needs a human decision before it is implemented.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
