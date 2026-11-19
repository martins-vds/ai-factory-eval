# BillingJob main uses a hard-coded two-member input

## Question
`BillingJob.main` bills only its literal `ana` and `ben` entries instead of loading the member roster or invoice data. Preserve, fix, or something else?

## Evidence
- Source: `legacy-billing/src/main/java/billing/BillingJob.java:26-30`
- Characterization: Source-only inspection (tier B); the executable entry point passes a fixed map containing `ana` with a $4.75 late fee and `ben` with no late fees. No runtime characterization was performed.
- Why it looks wrong: Running the monthly billing application cannot process any member data other than these two hard-coded examples.

## Impact
- Ledger capabilities: `billing.monthly-run`
- Blocks: Future billing implementation ticket(s) must depend on the human decision; BL-01 inventory is not blocked.

## Options
1. Preserve exactly (the target's executable entry point uses only these two members)
2. Fix (the target obtains the actual member invoices from an approved source)
3. Other
