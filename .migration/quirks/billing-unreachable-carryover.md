# Monthly billing cannot carry a valid invoice over

## Question
Should the monthly billing run charge the $3.00 membership fee even when a member has no late fees, making its carry-over branch unreachable?

## Evidence
- Source: `legacy-billing/src/main/java/billing/BillingJob.java:15-22`; `legacy-billing/src/main/java/billing/InvoiceCalculator.java:9-10,17-24,27-30`
- Characterization: an empty member invoice is $3.15 and `BillingJob.run` charges it; its output is `ben charged 3.15 ref approved-reference`.
- Why it looks wrong: every entry is totaled with `member=true`, so nonnegative fees yield a minimum total of $3.15, above the $1.00 charge threshold; the job's carry-over branch cannot be reached with valid invoice lines.

## Impact
- Ledger capabilities: `billing.monthly-run`, `billing.invoice-total`, `billing.chargeability`
- Blocks: a human ruling before implementing the monthly billing charge/carry-over behavior in the target.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
