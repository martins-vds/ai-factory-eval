# Quirk: POST /loans without form content type returns 500

## Question
Should a POST to `/loans` without form content type keep returning a Grizzly 500, or should the target reject it with a client error?

## Evidence
- Source: `legacy/src/main/java/lib/LoanResource.java:37-42` at `563c316ed51462b08fd6e58f3781a3c8b2890453`.
- Characterization: `curl -i -X POST http://127.0.0.1:18080/loans` returned HTTP 500 and a Grizzly error page. Sending an empty or partial `application/x-www-form-urlencoded` body returned HTTP 400 with `member and isbn are required`.
- Why it looks wrong: the same missing-input case is a 400 when sent as a form, but becomes a server error when the form media type is absent.

## Impact
- Ledger capabilities: loan creation request validation.
- Blocks: none until a target ticket depends on this decision.

## Options
1. Preserve the observed 500 for requests without form content type.
2. Reject the unsupported media type with a client error in the target.
3. Other
