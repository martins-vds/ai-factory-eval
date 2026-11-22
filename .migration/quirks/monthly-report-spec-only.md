# Monthly report spec has no implementation

## Question
The source includes a monthly lending report specification but says the separate product's code and runtime are no longer available. Should the migration implement the documented behavior, treat it as retired and out of scope, or do something else?

## Evidence
- Source: `document:legacy/docs/reports-spec.md`, `legacy/docs/reports-spec.md:1-9`
- Characterization: not applicable; the source states that no report code or runtime is available.
- Why it looks wrong: the report is documented as a capability in the source tree, but there is no executable behavior to observe or verify.

## Impact
- Ledger capabilities: `reports.monthly-spec`
- Blocks: any ticket that would implement or exclude the monthly report (not yet filed)

## Options
1. Preserve the documented specification as an in-scope, spec-derived report capability.
2. Treat the report as retired documentation and record an approved drop.
3. Other
