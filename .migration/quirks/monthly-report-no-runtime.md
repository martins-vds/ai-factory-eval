# Monthly report is specified but has no implementation

## Question
The legacy tree specifies a monthly lending report but says its separate product's code and runtime are unavailable; should the migration implement the documented report or treat it as retired?

## Evidence
- Source: `legacy/docs/reports-spec.md:1-9`
- Characterization: The document specifies prior-month scheduling, per-member counts and late fees, sorting, and omission rules, but provides no executable behavior to observe.
- Why it looks wrong: The capability is documented in scope but cannot be characterized from an implementation.

## Impact
- Ledger capabilities: `reports.monthly`
- Blocks: Scope decision for `reports.monthly` (ticket link pending orchestration).

## Options
1. Preserve exactly (implement the documented behavior and pin it with tests)
2. Fix (treat the report as retired; record the approved divergence in the ledger)
3. Other
