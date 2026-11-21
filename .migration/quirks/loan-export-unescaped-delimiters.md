# Loan export does not escape field delimiters

## Question
The loan export joins field values with semicolons and newlines without escaping them, while the lending endpoint accepts non-null values unchanged; preserve, fix, or something else?

## Evidence
- Source: `legacy/src/main/java/lib/LoanResource.java:38-42,52-55`; `legacy/docs/export-csv.md:3-4`
- Characterization: Source-only inference: a member or ISBN value containing `;` appears as extra columns, and a value containing a newline appears as an extra row; no runtime trace was recorded in SY-04.
- Why it looks wrong: The documented export is a fixed six-field, one-row-per-loan format, but the code allows values to break that shape.

## Impact
- Ledger capabilities: `loans.create`, `loans.export`
- Blocks: Implementation decisions for `loans.create` and `loans.export` (ticket links pending orchestration).

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it)
2. Fix (target diverges; the divergence is recorded in the ledger with this ticket as approval)
3. Other
