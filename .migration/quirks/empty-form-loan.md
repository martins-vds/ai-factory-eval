# Empty POST /loans returns 500

## Question
An empty `POST /loans` returns HTTP 500 rather than the 400 response the handler declares. Preserve, fix, or something else?

## Evidence
- Source: `legacy/src/main/java/lib/LoanResource.java:37-41` at `563c316ed51462b08fd6e58f3781a3c8b2890453`.
- Characterization: `curl -sS -i -X POST http://127.0.0.1:8080/loans` with no body returned `HTTP/1.1 500 Request failed.` and a 1031-byte Grizzly HTML error page.
- Why it looks wrong: the handler checks for a missing member or ISBN and explicitly returns HTTP 400 with `member and isbn are required\n`.

## Impact
- Ledger capabilities: characterization-harness, unit-integration-tests
- Blocks: target behavior for an empty loan-creation request until a human chooses whether to preserve or fix it.

## Options
1. Preserve exactly (target reproduces the quirk; a test pins it).
2. Fix (target returns 400; the divergence is recorded with this ticket as approval).
3. Other.
