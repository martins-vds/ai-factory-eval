# Repeated payment requests call the gateway again

## Question
Every `POST /payments/{id}` for an existing loan sends a new gateway request, with no local payment state or deduplication. Preserve this, require an idempotent gateway, or something else?

## Evidence
- Source: `function:legacy/src/main/java/lib/FinePayments.java:pay`, `legacy/src/main/java/lib/FinePayments.java:29-37`
- Characterization: two successful `POST /payments/L1` requests each returned HTTP 200 `charged`; the controlled gateway observed two bodyless `POST /charge?loan=L1` requests.
- Why it looks wrong: retrying a request may charge again; whether the external gateway deduplicates the loan ID is unspecified by the source.

## Impact
- Ledger capabilities: `payments.charge`
- Blocks: future migration tickets implementing this capability

## Options
1. Preserve exactly (each request calls the gateway; tests pin this behavior)
2. Fix (the target prevents duplicate charges or makes calls idempotent; the divergence is recorded with this ticket as approval)
3. Other
