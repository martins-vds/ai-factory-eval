# Blank loan fields pass the required-field check

## Question
`POST /loans` rejects null member or ISBN values but accepts empty strings. Preserve, fix, or something else?

## Evidence
- Source: `endpoint:legacy/src/main/java/lib/LoanResource.java:POST /loans` / `legacy/src/main/java/lib/LoanResource.java:37-42`
- Characterization: Predicted from source (not yet exercised): a request with both form fields present but empty passes the null check and proceeds to create a loan.
- Why it looks wrong: The error response says both fields are required, but the implementation enforces presence only, not non-blank values.

## Impact
- Ledger capabilities: `loans.create`, `loans.schema`
- Blocks: Any ticket implementing loan input validation; no plan ticket is assigned yet.

## Options
1. Preserve acceptance of blank values exactly.
2. Reject blank or whitespace-only member and ISBN values.
3. Other
