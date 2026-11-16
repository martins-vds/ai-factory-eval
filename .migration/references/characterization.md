# Legacy characterization — tier A

Source: `martins-vds/ai-factory-synthetic-target`, commit `563c316ed51462b08fd6e58f3781a3c8b2890453`, path `legacy/`. All 14 local files under `legacy/` were compared byte-for-byte with that pinned remote tree and matched.

The source is Java 17 / Maven, using Jersey 3.1.5 (JAX-RS) on Grizzly, Hibernate ORM 6.4.4 (JPA), and H2 2.2.224. `legacy/src/main/resources/META-INF/persistence.xml` configures an in-memory H2 database and loads the seed rows.

## Build and start

Ran from the repository root:

```sh
PORT=18080 ./legacy/run.sh
```

`legacy/run.sh` ran `mvn -q -B package -DskipTests`, then started `java -cp "target/classes:target/dependency/*" lib.App`. Maven exited successfully. The process logged `Lending Library listening on 18080` and bound the HTTP server to `0.0.0.0:18080`.

## Requests and observations

All requests used `http://127.0.0.1:18080`:

| Request | Observed response |
|---|---|
| `GET /loans` | `200`; seeded rows were returned in ID order: `L1;ana;9780134685991;2026-01-02;2026-01-16;`, `L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20`, `L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03`. |
| `GET /loans/L1` | `200`; `L1;ana;9780134685991;2026-01-02;2026-01-16;`. |
| `GET /about` | `200 text/html`; page title and heading were “About the Lending Library”; it states Monday–Saturday, 9:00–18:00 and 14-day loans. |
| `GET /loans/no-such-loan` | `404 text/plain`; body `no such loan`. |
| `GET /fees/L1` | `200 text/html`; due `2026-01-16`, `304` days late on the run date, fee capped at `$10.00`. |
| `POST /loans` with form `member=only` | `400 text/plain`; body `member and isbn are required`. |
| `POST /loans` with form `member=eval&isbn=9780000000000` | `201`; `L4;eval;9780000000000;2026-11-16;2026-11-30;`. |
| `POST /loans/L4/return` | `200`; response ended with returned date `2026-11-16`. |
| `POST /payments/missing` | `404 text/plain`; body `no such loan`; no gateway request was made for a missing loan. |

Commands used for the HTTP checks:

```sh
curl -sS -i http://127.0.0.1:18080/loans
curl -sS -i http://127.0.0.1:18080/loans/L1
curl -sS -i http://127.0.0.1:18080/about
curl -sS -i http://127.0.0.1:18080/loans/no-such-loan
curl -sS -i http://127.0.0.1:18080/fees/L1
curl -sS -i -X POST http://127.0.0.1:18080/loans -H 'Content-Type: application/x-www-form-urlencoded' -d 'member=only'
curl -sS -i -X POST http://127.0.0.1:18080/loans -H 'Content-Type: application/x-www-form-urlencoded' -d 'member=eval&isbn=9780000000000'
curl -sS -i -X POST http://127.0.0.1:18080/loans/L4/return
curl -sS -i -X POST http://127.0.0.1:18080/payments/missing
```

The valid-loan payment path was not called because it would contact the configured external gateway; only the missing-loan response was observed. The app ran against its real seeded H2 instance, and no files under `legacy/` were changed.
