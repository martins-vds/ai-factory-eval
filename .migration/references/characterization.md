# Legacy characterization

## Environment and tier

**Tier A.** The pinned Java 17 application built and started in this environment, and its HTTP endpoints returned live responses. The source files used for the run match commit `563c316ed51462b08fd6e58f3781a3c8b2890453`; `git diff --stat 563c316ed51462b08fd6e58f3781a3c8b2890453 HEAD -- legacy` reported no differences.

The legacy source is Java 17, JAX-RS 3.1 on Grizzly, JPA/Hibernate 6.4, and H2 2.2. No legacy test sources or test dependencies were present in `legacy/`.

## Commands and observations

1. Ran `java -version`: Temurin 17.0.21; ran `mvn -version`: Maven 3.10.1.
2. Ran `./legacy/run.sh` in `/home/runner/work/ai-factory-eval/ai-factory-eval`. Maven completed `mvn -q -B package -DskipTests`; Hibernate initialized `jdbc:h2:mem:library;DB_CLOSE_DELAY=-1`; Grizzly started on port 8080 and printed `Lending Library listening on 8080`.
3. While the server remained running on port 8080, ran:
   - `curl -sS -i http://127.0.0.1:8080/loans` -> 200, `text/plain`, three seeded semicolon-separated loan lines.
   - `curl -sS -i http://127.0.0.1:8080/loans/L1` -> 200 and `L1;ana;9780134685991;2026-01-02;2026-01-16;`.
   - `curl -sS -i http://127.0.0.1:8080/loans/missing` -> 404, `text/plain`, `no such loan`.
   - `curl -sS -i -X POST http://127.0.0.1:8080/loans` with no form fields -> 500 HTML `Request failed.`
   - `curl -sS -i -X POST -d member=test-member -d isbn=9780000000001 http://127.0.0.1:8080/loans` -> 201 and `L4;test-member;9780000000001;2026-11-21;2026-12-05;`.
   - `curl -sS -i -X POST http://127.0.0.1:8080/loans/L4/return` -> 200 and the L4 row with returned date `2026-11-21`.
   - `curl -sS -i -X POST http://127.0.0.1:8080/loans/missing/return` -> 404, `text/plain`, `no such loan`.
   - `curl -sS -i http://127.0.0.1:8080/fees/L1` -> 200, `text/html`, with due date `2026-01-16`, `309 day(s) late`, and fee `$10.00`.
   - `curl -sS -i http://127.0.0.1:8080/about` -> 200, `text/html`, with the exact About page title and lending hours/content from the live response.
   - `curl --max-time 10 -sS -i -X POST http://127.0.0.1:8080/payments/L1` -> 502, `text/plain`, `payment gateway unavailable` using the default reserved `.invalid` gateway.
   - `curl --max-time 10 -sS -i -X POST http://127.0.0.1:8080/payments/missing` -> 404, `text/plain`, `no such loan`.

The startup also logged Jersey warnings that each resource class was ignored as a provider, although the live routes above were reachable. No source files were changed. The seed used the in-memory H2 database. The server was stopped after endpoint exercise.
