# Legacy characterization — tier A

Source: `martins-vds/ai-factory-synthetic-target@563c316ed51462b08fd6e58f3781a3c8b2890453`, path `legacy/`.
The tracked files in the local `legacy/` directory were checked against the pinned commit's Git blob hashes.
The source was not modified.

## Build and start

From the repository root, ran:

```sh
./legacy/run.sh
```

The script ran `mvn -q -B package -DskipTests` successfully, then started the Java 17 application. Startup logged
`Lending Library listening on 8080`; Hibernate connected to `jdbc:h2:mem:library;DB_CLOSE_DELAY=-1` and initialized
the seeded database. The process remained in the foreground until stopped after the probes below. No legacy test
sources were found under `legacy/src/test`.

## HTTP probes

All requests used `curl` against `http://127.0.0.1:8080`. Dates below are the observed runtime date, 2026-11-16.

| Request | Input | Observed response |
|---|---|---|
| `GET /about` | — | `200`, `text/html`; returned the Lending Library about page with hours, 14-day loan period, and contact `desk@lending-library.invalid`. |
| `GET /loans` | — | `200`, `text/plain`; body: `L1;ana;9780134685991;2026-01-02;2026-01-16;` then `L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20` then `L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03`, each newline-terminated. |
| `GET /loans/L1` before return | — | `200`, `text/plain`; body: `L1;ana;9780134685991;2026-01-02;2026-01-16;\n`. |
| `GET /loans/L1` after return | — | `200`, `text/plain`; body: `L1;ana;9780134685991;2026-01-02;2026-01-16;2026-11-16\n`. |
| `GET /fees/1` | — | `404`, `text/html`; body: `<p>No such loan.</p>`. |
| `GET /fees/L1` | — | `200`, `text/html`; body: `<h1>Late fee for L1</h1><p>Due 2026-01-16, 304 day(s) late.</p><p class="fee">Fee: $10.00</p>`. |
| `POST /loans` | Form `member=reader-1&isbn=9780000000001` | `201`, `text/plain`; body: `L4;reader-1;9780000000001;2026-11-16;2026-11-30;\n`. |
| `POST /loans` | No body and no `Content-Type` header | `500 Request failed`, `text/html;charset=ISO-8859-1`; Grizzly's generic error page. |
| `POST /loans` | Empty `application/x-www-form-urlencoded` form | `400`, `text/plain`; body: `member and isbn are required\n`. |
| `POST /loans` | Form with only `member` or only `isbn` | `400`, `text/plain`; body: `member and isbn are required\n`. |
| `POST /loans/L1/return` | — | `200`, `text/plain`; body: `L1;ana;9780134685991;2026-01-02;2026-01-16;2026-11-16\n`. |
| `GET /fees/L1` after return | — | Still reported 304 days late and a capped `$10.00` fee. |
| `GET /payments/1` | — | `405`; `Allow: POST,OPTIONS`. |
| `POST /payments/does-not-exist` | — | `404`, `text/plain`; body: `no such loan\n`; the missing-loan path returns before contacting the payment gateway. |

The success path for an existing-loan payment was not called because it would invoke the external payment gateway.
The 500 for a POST without a form media type is recorded as a quirk draft; the supported empty form returns 400.
