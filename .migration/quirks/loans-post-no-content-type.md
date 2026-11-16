# POST /loans without a form Content-Type returns 500

## Question
When `POST /loans` has no body and no `Content-Type`, the source returns a generic HTTP 500. Preserve, fix, or something else?

## Evidence
- Source: `legacy/src/main/java/lib/LoanResource.java:37-42` accepts `member` and `isbn` as form parameters and explicitly returns 400 when either is missing.
- Characterization: `curl -sS -i -X POST http://127.0.0.1:8080/loans` returned `500 Request failed` with a Grizzly HTML error page. Sending the same empty input as `application/x-www-form-urlencoded` returned `400` with `member and isbn are required`.
- Why it looks wrong: the request is not a form submission, but the generic 500 differs from the method's explicit missing-field validation response.

## Impact
- Ledger capabilities: loan creation endpoint.
- Blocks: target implementation of `POST /loans` until the human chooses an option.

## Options
1. Preserve exactly (the target returns the same 500 for a request without form media type).
2. Fix (the target returns a client error; record the approved divergence).
3. Other.
