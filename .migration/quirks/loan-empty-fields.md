# Empty loan fields are accepted

## Question
The source rejects missing `member` or `isbn` parameters but accepts empty strings; preserve empty values, reject them, or something else?

## Evidence
- Source: `method:legacy/src/main/java/lib/LoanResource.java:LoanResource.lend`, `legacy/src/main/java/lib/LoanResource.java:38-43`
- Characterization: tier A observed `member=` and `isbn=` creating `L5;;;2026-11-22;2026-12-06;\n` with HTTP 201 (`goldens/edges.json`, `empty-loan-fields`).
- Why it looks wrong: the error response says both fields are required, but the source distinguishes only missing parameters from empty values.

## Impact
- Ledger capabilities: `loan.lend`
- Blocks: future migration tickets implementing this capability (not yet filed)

## Options
1. Preserve exactly (accept empty values; tests pin this behavior)
2. Reject empty values (record the divergence with this ticket as approval)
3. Other
