# Monthly report specification remains without its retired module

## Question
`legacy/docs/reports-spec.md` specifies a monthly lending report, but the document says its separate product's code and runtime are no longer available. Should the target implement the remaining specification, retain it as documentation only, or treat it as retired?

## Evidence
- Source: `document:legacy/docs/reports-spec.md` / `legacy/docs/reports-spec.md:1-9`
- Characterization: The source document specifies a first-day-of-month report for the previous month with per-member lending, late-return, and fee totals; no executable reporting implementation is present in the pinned source.
- Why it looks wrong: A complete report specification survives without the module it describes, leaving its intended migration disposition unclear.

## Impact
- Ledger capabilities: `docs.monthly-report`
- Blocks: Any ticket that would implement or explicitly omit the monthly report; no plan ticket is assigned yet.

## Options
1. Preserve the report capability by rebuilding it from the documented specification.
2. Keep the document but record the report as retired only with human approval.
3. Other
