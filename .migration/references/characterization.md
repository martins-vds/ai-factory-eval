# Legacy characterization

## Environment and tier

**Tier A.** The pinned Java 17 application builds and starts in this environment, and its HTTP endpoints returned live responses. The source files used for the run match the requested pinned source; for example, the Git blob IDs for `legacy/pom.xml`, `legacy/src/main/java/lib/App.java`, and `legacy/src/main/java/lib/FinePayments.java` are `f239b347241beb70eb0c9cad14632f2e81e25d2c`, `4e5a396529b82c3190b368c4bdcd3c5cde65a70b`, and `b2040f686c4cf77b217455d726a6eb14c9121e26`, respectively.

The legacy source is Java 17, JAX-RS 3.1 on Grizzly, JPA/Hibernate 6.4, and H2 2.2. No legacy test sources or test dependencies were present in `legacy/`.

## Commands and observations

1. Ran `timeout 60s ./legacy/run.sh`. Maven's `package -DskipTests` completed; Hibernate initialized the H2 in-memory database and Grizzly started on port 8080 (`Lending Library listening on 8080`). The command exited 124 when the timeout stopped the long-running server. Startup logged Jersey warnings that each resource class was ignored as a provider, although requests below still reached the routes.
2. Ran `PORT=18080 timeout --signal=INT 25s ./legacy/run.sh`, then issued the requests below with `curl -i` against `http://127.0.0.1:18080`. The runner started on port 18080. `GET /loans` returned 200, `text/plain`:

   ```text
   L1;ana;9780134685991;2026-01-02;2026-01-16;
   L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20
   L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03
   ```

   `GET /loans/L1` returned 200 and `L1;ana;9780134685991;2026-01-02;2026-01-16;`. `GET /fees/L1` returned 200, `text/html`, and `<h1>Late fee for L1</h1><p>Due 2026-01-16, 303 day(s) late.</p><p class="fee">Fee: $10.00</p>`. `GET /about` returned 200, `text/html`, with this exact body:

   ```html
   <!doctype html>
   <html lang="en">
   <head><meta charset="utf-8"><title>About the Lending Library</title></head>
   <body>
     <h1>About the Lending Library</h1>
     <p>Open Monday to Saturday, 9:00 to 18:00. Books are lent for 14 days.</p>
     <p>Contact: desk@lending-library.invalid</p>
   </body>
   </html>
   ```

   `POST /loans` with form fields `member=characterization&isbn=9780000000000` returned 201 and `L4;characterization;9780000000000;2026-11-15;2026-11-29;`. `POST /loans/L1/return` returned 200 and the L1 row with returned date `2026-11-15`.
3. Ran `PORT=18081 timeout --signal=INT 20s ./legacy/run.sh`, then issued the following `curl -i` requests against `http://127.0.0.1:18081`:
   - `GET /loans/unknown` returned 404, `text/plain`, `no such loan`.
   - `GET /fees/unknown` returned 404, `text/html`, `<p>No such loan.</p>`.
   - `POST /loans` with an empty form returned 400, `text/plain`, `member and isbn are required`.
   - `POST /payments/unknown` returned 404, `text/plain`, `no such loan`.
   - `POST /payments/L1` used the default reserved `.invalid` gateway and returned 502, `text/plain`, `payment gateway unavailable`.

No source files were changed. Runs used the seeded in-memory H2 database and were stopped by their timeouts.
