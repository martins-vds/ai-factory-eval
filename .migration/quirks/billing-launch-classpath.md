# Billing launcher may omit runtime dependencies

## Question
`run.sh` launches with `target/dependency/*`, but the POM does not configure dependency copying into that directory; should the launcher add that step or use another runtime classpath?

## Evidence
- Source: `legacy-billing/run.sh:5-6` and `legacy-billing/pom.xml:20-33`
- Characterization: source-predicted: `mvn package` is followed by a Java classpath containing `target/classes` and `target/dependency/*`; the POM declares the Northgate client but no dependency-copy plugin or execution. Not executed in BL-01 because the full build requires the vendor's private Maven repository.
- Why it looks wrong: the billing entrypoint references `VaultClient`, but the run script does not add Maven's local dependency cache or otherwise populate its `target/dependency` classpath directory.

## Impact
- Ledger capabilities: `billing.job-launch`
- Blocks: any target implementation of the billing launcher until the runtime dependency strategy is decided; characterization may record the behavior.

## Options
1. Preserve exactly (target uses the same classpath behavior; a test pins it)
2. Fix (target packages or locates runtime dependencies correctly; the divergence is recorded in the ledger with this ticket as approval)
3. Other
