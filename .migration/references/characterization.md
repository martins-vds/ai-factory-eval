# Legacy characterization evidence

The source pin is `martins-vds/ai-factory-synthetic-target@563c316ed51462b08fd6e58f3781a3c8b2890453`, path `legacy`. The pinned tree ID for `legacy/` and the current checkout's `legacy/` tree ID both resolved to `1e683e0091beb079121c2ab6d223573ae29186ae`; `git diff --stat 563c316ed51462b08fd6e58f3781a3c8b2890453 -- legacy` was empty. The source was not modified.

## Build and launch

To keep build output out of the read-only source tree, an unchanged copy was used:

```sh
mkdir -p /tmp/sy01-characterization
cp -a /home/runner/work/ai-factory-eval/ai-factory-eval/legacy /tmp/sy01-characterization/
cd /tmp/sy01-characterization && PORT=18080 ./legacy/run.sh
```

`legacy/run.sh` ran `mvn -q -B package -DskipTests`, then `java -cp "target/classes:target/dependency/*" lib.App`. Maven packaging succeeded, and the server logged `Lending Library listening on 18080`. Hibernate connected to `jdbc:h2:mem:library;DB_CLOSE_DELAY=-1`. Startup emitted Jersey warnings that the registered resource classes would be ignored; the endpoint results below show that the loans, fees, and about routes did respond.

The runtime was OpenJDK 17.0.21 and Maven 3.10.0.

## HTTP probes

Requests used `curl -sS -i --max-time 4` against `http://127.0.0.1:18080`; POST requests used `curl -sS -i --max-time 4 -X POST`, adding the listed form data where applicable. The valid payment probe used `--max-time 10`.

| Request | Observed result |
|---|---|
| `GET /` | `404 Not Found`, empty body. |
| `GET /loans` | `200 OK`, `text/plain`; body `L1;ana;9780134685991;2026-01-02;2026-01-16;\nL2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20\nL3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03\n`. |
| `GET /loans/demo` | `404 Not Found`, body `no such loan\n`. |
| `GET /late-fees`, `GET /payments`, `GET /about.html` | Each returned `404 Not Found`, empty body. |
| `GET /about` | `200 OK`, `text/html`; body `<!doctype html>\n<html lang="en">\n<head><meta charset="utf-8"><title>About the Lending Library</title></head>\n<body>\n  <h1>About the Lending Library</h1>\n  <p>Open Monday to Saturday, 9:00 to 18:00. Books are lent for 14 days.</p>\n  <p>Contact: desk@lending-library.invalid</p>\n</body>\n</html>\n`. |
| `GET /fees/L1` | `200 OK`, `text/html`; body `<h1>Late fee for L1</h1><p>Due 2026-01-16, 308 day(s) late.</p><p class="fee">Fee: $10.00</p>`. |
| `GET /fees/L2` | `200 OK`, `text/html`; body `<h1>Late fee for L2</h1><p>Due 2026-01-24, 0 day(s) late.</p><p class="fee">Fee: $0.00</p>`. |
| `GET /fees/L3` | `200 OK`, `text/html`; body `<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p><p class="fee">Fee: $4.75</p>`. |
| `GET /fees/missing` | `404 Not Found`, body `<p>No such loan.</p>`. |
| `POST /loans` with `member=eval-user&isbn=9780000000001` | `201 Created`, body `L4;eval-user;9780000000001;2026-11-20;2026-12-04;\n`. |
| `POST /loans` with only `isbn=9780000000001` | `400 Bad Request`, body `member and isbn are required\n`. |
| `POST /loans/L4/return` | `200 OK`, body `L4;eval-user;9780000000001;2026-11-20;2026-12-04;2026-11-20\n`. |
| `GET /loans/L4` after return | `200 OK`, returned the same row with the return date. |
| `POST /payments/missing` | `404 Not Found`, body `no such loan\n`. |
| `POST /payments/L1` | `502 Bad Gateway`, body `payment gateway unavailable\n` using the default gateway URL. |

These observations support characterization tier A: the source built, ran, and exposed HTTP behavior that could be observed through its external interface. No source test tree was present, and no payment gateway success case was available in this environment.
