# Payment interruption is swallowed

## Question
If the payment gateway call is interrupted, the source catches `InterruptedException` and returns HTTP 502 without restoring the thread's interrupted status. Preserve this error behavior, restore the interrupt, or something else?

## Evidence
- Source: `function:legacy/src/main/java/lib/FinePayments.java:pay`, `legacy/src/main/java/lib/FinePayments.java:34-40`
- Characterization: tier A observed a refused controlled-gateway connection returning HTTP 502 with `payment gateway unavailable\n`; interruption itself was not separately exercised. See `.migration/characterization/source/goldens/gateway.json`.
- Why it looks wrong: clearing the interrupt can prevent the server from promptly stopping or cancelling interrupted request work.

## Impact
- Ledger capabilities: `integration.payment-gateway`, `payment.gateway-errors`
- Blocks: future migration tickets implementing these capabilities (not yet filed)

## Options
1. Preserve exactly (return 502 and swallow interruption; tests pin this behavior)
2. Fix (the target preserves/cancels on interruption; the divergence is recorded with this ticket as approval)
3. Other
