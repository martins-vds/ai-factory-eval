# Monthly report specification has no implementation

## Question
The legacy tree retains a monthly-report specification but says its separate product's code and runtime are unavailable. Migrate the specified report, preserve documentation only, or something else?

## Evidence
- Source: `document:legacy/docs/reports-spec.md`, `legacy/docs/reports-spec.md:1-9`
- Characterization: no executable report behavior is present to observe; only the document remains.
- Why it looks wrong: the specification describes scheduled, calculated report output but the source tree contains no implementation or runtime for it.

## Impact
- Ledger capabilities: `reporting.monthly-spec`
- Blocks: any ticket that would implement or explicitly exclude the report

## Options
1. Preserve exactly (retain the specification only; no report is implemented)
2. Implement the spec in the target (record the new capability and its evidence)
3. Other
