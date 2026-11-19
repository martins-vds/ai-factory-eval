# Billing member processing order is not fixed

## Question
Should the billing entrypoint preserve a fixed order for charging and reporting the hardcoded members, or is the `Map.of` iteration order acceptable? Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/BillingJob.java:26-31`
- Characterization: The source lists `ana` before `ben`, but a separate-JVM run of `BillingCharacterizationTest.entryPointReadsEnvironmentAndUsesFixedMembersRegardlessOfArguments` emitted `ben` before `ana`.
- Why it looks wrong: Member processing order determines the order of external card charges and console output, but the entrypoint supplies a `Map.of` whose iteration order is not explicitly controlled.

## Impact
- Ledger capabilities: `billing.job-entrypoint`, `billing.job-processing`
- Blocks: Member-billing implementation ticket(s), to be identified by the coordinator.

## Options
1. Preserve exactly (the target does not promise a fixed order; a test pins only membership and results)
2. Fix (the target uses a defined order; the divergence is recorded in the ledger with this ticket as approval)
3. Other
