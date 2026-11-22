# Monthly report is specification-only

## Question
The source contains a monthly lending report specification but no executable reporting module; should the target implement it, preserve only the documentation, or something else?

## Evidence
- Source: `document:legacy/docs/reports-spec.md`, `legacy/docs/reports-spec.md:1-6`
- Characterization: Tier-C specification: run on the first day for the previous month; emit member id, loans started, loans returned late, and late fees in cents; omit members without monthly loans; sort by fees descending then member id.
- Why it looks wrong: the source product has no runnable implementation for this documented capability, so the target requirement is ambiguous.

## Impact
- Ledger capabilities: `reports.monthly`
- Blocks: future migration tickets implementing this capability (not yet filed)

## Options
1. Preserve exactly (retain the specification without implementing reporting)
2. Implement the report (record the divergence from the retired source module)
3. Other
