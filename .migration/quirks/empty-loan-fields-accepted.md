# Empty loan fields are accepted

## Question
`POST /loans` rejects a missing member or ISBN but accepts both fields as empty strings; preserve, fix, or something else?

## Evidence
- Source: `legacy/src/main/java/lib/LoanResource.java:37-43`
- Characterization: `POST /loans` with `member=` and `isbn=` returned 201 with `L5;;;2026-11-21;2026-12-05;`; the following list included the row. See `.migration/characterization/source/goldens/http.json` (`POST /loans empty fields`, `GET /loans after empty fields`).
- Why it looks wrong: The endpoint reports that both values are required when omitted, but does not reject blank values.

## Impact
- Ledger capabilities: `loans.create`
- Blocks: Implementation decision for `loans.create` (ticket link pending orchestration).

## Options
1. Preserve exactly (empty values remain valid; a test pins this behavior)
2. Fix (the target rejects empty values; the divergence is recorded with this ticket as approval)
3. Other
