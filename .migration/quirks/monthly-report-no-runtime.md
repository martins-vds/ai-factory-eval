# Monthly lending report specification has no runtime implementation

## Question
The legacy source contains a specification for a monthly lending report, but no report code or runtime exists. Preserve that specification as a missing capability, or replace/drop it with human approval?

## Evidence
- Source: `legacy/docs/reports-spec.md:1-8`
- Graph: `document:legacy/docs/reports-spec.md`
- Characterization: no runnable reporting module or test exists in the pinned source.
- Why it looks wrong: the specification is observable source behavior only in documentation, while the application has no route or scheduled job that can produce it.

## Impact
- Ledger capabilities: `monthly-report.spec`
- Blocks: tickets that implement or remove monthly reporting

## Options
1. Preserve exactly (implement the specified report in the target)
2. Fix (replace or redefine the report behavior)
3. Other
