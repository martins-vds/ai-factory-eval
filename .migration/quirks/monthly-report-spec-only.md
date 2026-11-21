# Monthly report is specification-only

## Question
The source contains a monthly lending report specification but says its separate product's code and runtime are no longer available. Should the report be implemented from the specification, excluded from the migration, or something else?

## Evidence
- Source: `document:legacy/docs/reports-spec.md`, `legacy/docs/reports-spec.md:1-9`
- Characterization: tier-C specification says to run on the first day for the previous month and emit per-member counts and late fees; the pinned graph has no monthly-report endpoint or implementation node.
- Why it looks wrong: the specification describes behavior without a runnable implementation, so silently omitting it or inventing behavior would make an unapproved scope decision.

## Impact
- Ledger capabilities: `report.monthly-spec`
- Blocks: any ticket to implement or explicitly omit the report

## Options
1. Preserve the source's absence of a report (do not migrate it)
2. Implement the documented report as an approved specification-derived capability
3. Other
