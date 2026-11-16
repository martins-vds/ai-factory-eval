# Legacy characterization

Source: `martins-vds/ai-factory-synthetic-target` at `563c316ed51462b08fd6e58f3781a3c8b2890453`, path `legacy/`.
Run on 2026-11-16 with OpenJDK 17.0.21 and Apache Maven 3.10.0.

## Commands and observations

From the repository root, I ran:

```sh
PORT=18080 ./legacy/run.sh
```

The script completed `mvn -q -B package -DskipTests`, started Hibernate against `jdbc:h2:mem:library;DB_CLOSE_DELAY=-1`, and printed `Lending Library listening on 18080`. It remained running in the foreground. Startup logged warnings that the four registered resource instances were ignored; the endpoint requests below nevertheless returned the application responses.

I then ran HTTP requests against `http://127.0.0.1:18080` using `curl -sS -i -X <method>`. For the successful loan creation, I also supplied `-d 'member=test&isbn=9780000000000'`; for the missing-form case, I supplied no body. The observed status and response bodies were:

| Request | Observed response |
| --- | --- |
| `GET /loans` | `200`; seeded rows `L1;ana;9780134685991;2026-01-02;2026-01-16;`, `L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20`, and `L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03`, each newline-terminated. |
| `GET /loans/L1` | `200`; `L1;ana;9780134685991;2026-01-02;2026-01-16;` |
| `GET /loans/NOPE` | `404`; `no such loan` |
| `GET /about` | `200`; HTML titled `About the Lending Library`, stating Monday–Saturday 9:00–18:00, a 14-day lending period, and `desk@lending-library.invalid`. |
| `GET /fees/L1` | `200`; due date `2026-01-16`, `304 day(s) late`, fee `$10.00`. |
| `GET /fees/NOPE` | `404`; `<p>No such loan.</p>` |
| `POST /loans` with `member=test&isbn=9780000000000` | `201`; `L4;test;9780000000000;2026-11-16;2026-11-30;` |
| `POST /loans/L1/return` | `200`; `L1;ana;9780134685991;2026-01-02;2026-01-16;2026-11-16` |
| `POST /loans/NOPE/return` | `404`; `no such loan` |
| `POST /payments/NOPE` | `404`; `no such loan` |
| `POST /payments/L1` | `502`; `payment gateway unavailable` |
| `POST /loans` without form data | `500`; Grizzly `Request failed.` HTML response. |

The run therefore meets characterization tier A: the legacy environment is available and the running application can be exercised over HTTP. The source has no characterization test suite.
