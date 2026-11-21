# Restart resets loan data

## Question
At every application startup, the source creates an in-memory H2 database with a `drop-and-create` schema and reloads the three seed loans. Preserve this reset-on-restart behavior, make loans persistent, or something else?

## Evidence
- Source: `config:legacy/src/main/resources/META-INF/persistence.xml`, `legacy/src/main/resources/META-INF/persistence.xml:6-10`
- Characterization: the tier-A restart scenario observed L4 and L5 before restart; after the app restarted, GET /loans returned only the original L1, L2, and L3 seed records.
- Why it looks wrong: loans added or returned while the app runs are discarded when it restarts, despite the interface allowing users to create and update loans.

## Impact
- Ledger capabilities: `data.loan-storage`, `data.seed-records`, `application.startup`
- Blocks: future migration tickets implementing these capabilities (not yet filed)

## Options
1. Preserve exactly (the target resets its data on startup; tests pin this behavior)
2. Fix (the target persists loan data; the divergence is recorded with this ticket as approval)
3. Other
