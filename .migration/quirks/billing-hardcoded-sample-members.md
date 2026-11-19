# Billing entrypoint processes only hard-coded sample members

## Question
`BillingJob.main` supplies only the hard-coded `ana` and `ben` entries instead of loading the member roster; preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/BillingJob.java:26-30`
- Characterization: Source-only trace, not executed in BL-01: invoking `main` with valid credentials passes only `ana` (one $4.75 late fee) and `ben` (no late fees) to `run`.
- Why it looks wrong: A monthly billing entrypoint appears to omit all members other than these two fixed examples.

## Impact
- Ledger capabilities: `billing.job-entrypoint`
- Blocks: migration of the executable entrypoint pending a human ruling

## Options
1. Preserve exactly (target reproduces the hard-coded entries; a test pins them)
2. Fix (target loads actual member billing entries; record the approved divergence)
3. Other
