# Legacy characterization

## Source pin and runtime

The source is `martins-vds/ai-factory-synthetic-target`, commit
`563c316ed51462b08fd6e58f3781a3c8b2890453`, under `legacy/`. The tracked files in the local
`legacy/` tree were compared with the pinned GitHub tree; their Git blob IDs matched. The separate
`.source/` gitlink is not correctly pinned: it resolves to
`10357e9e1cb6de3dffdf43da70e1727464c0db87`, not the source SHA in this profile.

Runtime versions: OpenJDK 17.0.21, Maven 3.10.0, Python 3.13.18, and curl. Maven builds with
`mvn -q -B package -DskipTests` as invoked by `legacy/run.sh`. The Java application uses Jersey
3.1.5, Hibernate 6.4.4.Final, Grizzly 4.0.1, and H2 2.2.224.

## Commands and observations

1. Ran `PORT=18080 ./legacy/run.sh`. Maven packaging completed, Hibernate connected to
   `jdbc:h2:mem:library;DB_CLOSE_DELAY=-1`, and the service printed
   `Lending Library listening on 18080`.
2. Ran `curl -fsS http://127.0.0.1:18080/about`: returned the HTML title “About the Lending
   Library”, Monday–Saturday 9:00–18:00 opening hours, 14-day lending policy, and
   `desk@lending-library.invalid`.
3. Ran `curl -sS -i http://127.0.0.1:18080/loans`: HTTP 200, `text/plain`, with the three
   seeded lines:

   ```text
   L1;ana;9780134685991;2026-01-02;2026-01-16;
   L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20
   L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03
   ```

4. Ran `curl -sS -i http://127.0.0.1:18080/loans/L1`: HTTP 200 with
   `L1;ana;9780134685991;2026-01-02;2026-01-16;`. Ran
   `curl -sS -i http://127.0.0.1:18080/loans/missing`: HTTP 404, `no such loan`.
5. Ran `curl -sS -i http://127.0.0.1:18080/fees/L2`: HTTP 200,
   `<h1>Late fee for L2</h1><p>Due 2026-01-24, 0 day(s) late.</p><p class="fee">Fee: $0.00</p>`.
   Ran `curl -sS -i http://127.0.0.1:18080/fees/L1`: HTTP 200,
   `<h1>Late fee for L1</h1><p>Due 2026-01-16, 303 day(s) late.</p><p class="fee">Fee: $10.00</p>`.
   Ran `curl -sS -i http://127.0.0.1:18080/fees/missing`: HTTP 404,
   `<p>No such loan.</p>`.
6. Ran `curl -sS -i -X POST -d 'member=eval-member&isbn=9780000000001' http://127.0.0.1:18080/loans`:
   HTTP 201, creating `L4` due 2026-11-29. Ran
   `curl -sS -i -X POST http://127.0.0.1:18080/loans/L4/return`: HTTP 200 and saved
   2026-11-15 as the return date.
7. Restarted the built app on port 18081. Ran
   `curl -sS -i -X POST -H 'Content-Type: application/x-www-form-urlencoded' --data '' http://127.0.0.1:18081/loans`:
   HTTP 400, `member and isbn are required`. Ran
   `curl -sS -i -X POST http://127.0.0.1:18081/loans` without a form content type: HTTP 500 from
   Grizzly/Jersey (`@FormParam` requires `application/x-www-form-urlencoded`).
8. Ran `curl -sS -i -X POST http://127.0.0.1:18080/payments/missing`: HTTP 404,
   `no such loan`. Ran `curl --max-time 25 -sS -i -X POST http://127.0.0.1:18080/payments/L1`:
   HTTP 502, `payment gateway unavailable`.

The app was stopped after probing. `legacy/src/test` is absent; the Maven command skips tests.
