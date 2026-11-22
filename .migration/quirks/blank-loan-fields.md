# Blank loan fields pass validation

## Question
When `POST /loans` supplies empty `member` or `isbn` values, the source accepts them because it rejects only null values. Preserve this, reject blanks, or something else?

## Evidence
- Source: `endpoint:legacy/src/main/java/lib/LoanResource.java:POST /loans`, `legacy/src/main/java/lib/LoanResource.java:38-43`
- Characterization: tier A observed `member=` and `isbn=` returning HTTP 201 and `L5;;;2026-11-22;2026-12-06;`; see `.migration/characterization/source/goldens/http.json` (`lend-empty-fields`) and `.migration/evidence/SY-05/characterization.md`.
- Why it looks wrong: the endpoint reports that both fields are required but treats an empty string as present.

## Impact
- Ledger capabilities: `loan.lend`
- Blocks: future migration tickets implementing this capability (not yet filed)

## Options
1. Preserve exactly (empty fields are accepted; a test pins this behavior)
2. Fix (reject blank fields; record the approved divergence in the ledger)
3. Other
