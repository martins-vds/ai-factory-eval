# Concurrent lends can allocate the same loan identifier

## Question
`LoanRepository.lend` creates an id from the current row count plus one, so overlapping creates can choose the same primary key. Preserve, fix, or something else?

## Evidence
- Source: `method:legacy/src/main/java/lib/LoanRepository.java:LoanRepository.lend` / `legacy/src/main/java/lib/LoanRepository.java:27-34`
- Characterization: Predicted from source (not yet exercised): with `n` rows, two overlapping creates can both count `n` and attempt to persist `L(n+1)`.
- Why it looks wrong: A count-based identifier is not unique under concurrent writes and can also reuse an identifier if rows are removed outside the exposed API.

## Impact
- Ledger capabilities: `loans.create`, `loans.repository`
- Blocks: Any ticket implementing loan creation; no plan ticket is assigned yet.

## Options
1. Preserve the count-based behavior exactly.
2. Use a collision-safe identifier strategy.
3. Other
