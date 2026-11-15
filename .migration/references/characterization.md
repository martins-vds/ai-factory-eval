# Legacy characterization (tier A)

The source is the Java 17/JAX-RS 3.1 application in `legacy/`, built with Maven, Hibernate ORM 6.4 and H2 2.2. The source SHA supplied for this task is `563c316ed51462b08fd6e58f3781a3c8b2890453`. GitHub returned that commit; the local `legacy/run.sh`, `App.java`, and `LoanResource.java` blob hashes match the pinned commit's corresponding files. The injected `.source` checkout is currently shallow at `47fff80a28ba4e72e35eb5ffb598aa0844ecf8c5` and does not contain the requested commit object; refresh it to the pinned SHA before bootstrap validation.

## Commands and observations

- `./run.sh` from the repository root failed with exit 127 (`No such file or directory`); the script is under `legacy/`.
- `legacy/run.sh` from the repository root built the Maven package and started the app on port 8080. Hibernate connected to `jdbc:h2:mem:library;DB_CLOSE_DELAY=-1`; Grizzly reported `Lending Library listening on 8080`. Jersey logged warnings that the registered resource instances did not implement provider interfaces, but the routes below responded.
- `curl -sS -i http://127.0.0.1:8080/loans` returned 200 `text/plain` with:

  ```text
  L1;ana;9780134685991;2026-01-02;2026-01-16;
  L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20
  L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03
  ```

- `curl -sS -i http://127.0.0.1:8080/loans/L1` returned 200 and the L1 semicolon-separated row. `/loans/unknown` returned 404 `no such loan`.
- `curl -sS -i http://127.0.0.1:8080/fees/L3` returned 200 HTML with `Due 2025-12-15, 19 day(s) late.` and `Fee: $4.75`. `/fees/not-a-loan` returned 404 `<p>No such loan.</p>`.
- `curl -sS -i -X POST http://127.0.0.1:8080/payments/L3` returned 502 `payment gateway unavailable` with the default invalid gateway URL.
- `curl -sS -i http://127.0.0.1:8080/about` returned 200 HTML identifying the Lending Library, Monday–Saturday 9:00–18:00 opening hours, 14-day loans, and `desk@lending-library.invalid`.
- `curl -sS -i -X POST -d member=dee -d isbn=123 http://127.0.0.1:8080/loans` returned 201 with `L4;dee;123;2026-11-15;2026-11-29;`.
- `curl -sS -i -X POST http://127.0.0.1:8080/loans/L1/return` returned 200 and recorded `2026-11-15`. Repeating the same request also returned 200 with the saved date unchanged; `/loans/no-such/return` returned 404 `no such loan`.

The endpoint probes ran against the live process launched by `legacy/run.sh`. The temporary in-memory database was discarded when the process stopped; no source files were changed.
