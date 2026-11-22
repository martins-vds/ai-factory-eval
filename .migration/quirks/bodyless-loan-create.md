# A bodyless loan create returns 500

## Question
`POST /loans` with no body returns HTTP 500, while a form with either required field missing returns HTTP 400. Preserve this distinction, normalize it, or something else?

## Evidence
- Source: `endpoint:legacy/src/main/java/lib/LoanResource.java:POST /loans` / `legacy/src/main/java/lib/LoanResource.java:37-43`
- Characterization: tier A observed a bodyless `POST /loans` returning HTTP 500 with Grizzly's HTML `Request failed.` response; a request with only `isbn` or only `member` returned HTTP 400 with `member and isbn are required\n`. See `.migration/evidence/runs/SY-05.md` (`missing-field-probe`).
- Why it looks wrong: a request with no fields bypasses the route's required-field response and instead becomes a server error, unlike requests missing only one field.

## Impact
- Ledger capabilities: `loans.create`
- Blocks: Any ticket implementing loan creation until a human decides how to handle the bodyless request.

## Options
1. Preserve the observed 500 for a bodyless request and 400 for partial forms.
2. Return the required-field 400 response for all missing-field requests.
3. Other
