# Loan creation without form content type returns 500

## Question
When `POST /loans` has no request body or form content type, the source returns a Grizzly HTTP 500 page instead of the handler's HTTP 400 validation response. Preserve this, return 400/415, or something else?

## Evidence
- Source: `method:legacy/src/main/java/lib/LoanResource.java:LoanResource.lend`, `legacy/src/main/java/lib/LoanResource.java:38-43`
- Characterization: `POST /loans` with no body and no `Content-Type` returned HTTP 500 with the Grizzly 4.0.1 error page in `.migration/characterization/source/goldens/http.json`.
- Why it looks wrong: the handler explicitly returns 400 when either form parameter is null, but the framework produces a server error before that validation runs.

## Impact
- Ledger capabilities: `loan.create`
- Blocks: future migration tickets implementing loan creation (not yet filed)

## Options
1. Preserve exactly (the request returns the framework's 500 page)
2. Fix (return a client error before invoking the handler; record the approved divergence in the ledger)
3. Other
