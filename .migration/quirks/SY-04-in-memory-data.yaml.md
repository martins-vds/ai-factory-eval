# In-memory H2 data is discarded and reseeded at every process start

## Question
The legacy process uses H2 in-memory storage with `drop-and-create` and sample seed data. Preserve or fix this behavior in the target?

## Evidence
- Source: `legacy/src/main/resources/META-INF/persistence.xml:1-17`
- Graph: `config:legacy/src/main/resources/META-INF/persistence.xml`
- Characterization: no characterization is available yet; source configuration shows process restart creates a new empty schema and reloads seed rows.

## Why it looks wrong
New loans and return edits disappear after restart, while `LOAN` seed rows reappear. A target with durable data may diverge from observable legacy restart behavior.

## Impact
- Ledger capabilities: `structural.loan-persistence`, `data.loan-record-store`, `data.loan-seed`
- Blocks: implementation decisions for persistence and restart behavior

## Options
1. Preserve exactly (target reproduces reset-and-reseed behavior)
2. Fix (target persists data across restarts)
3. Other
