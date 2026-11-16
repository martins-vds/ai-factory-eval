# Legacy characterization

## Stack

The source is a Java 17 Maven application using Jersey 3.1.5/JAX-RS 3.1, Hibernate ORM 6.4.4/JPA 3.1, and H2 2.2.224. It serves REST and HTML routes from Grizzly; its database is `jdbc:h2:mem:library;DB_CLOSE_DELAY=-1` and its records are seeded from `META-INF/seed.sql`. The payment route calls an external HTTP gateway configured by `PAYMENT_GATEWAY_URL`. Source files are UTF-8.

The requested target is Python 3.13 with Django 5, Django templates, and PostgreSQL 17.

## Tier A evidence

On 2026-11-16, ran `legacy/run.sh` with `PORT=18080` and `PAYMENT_GATEWAY_URL=http://127.0.0.1:9`. Maven packaged the application and the server started on port 18080. Requests were sent with Python's standard-library `urllib` to `http://127.0.0.1:18080`:

| Request | Result |
| --- | --- |
| `GET /loans` | HTTP 200; returned seeded loans L1, L2, and L3 |
| `GET /loans/L1` | HTTP 200; returned L1 |
| `GET /loans/NOPE` | HTTP 404; `no such loan` |
| `GET /fees/L3` | HTTP 200; showed 19 days late and `Fee: $4.75` |
| `GET /fees/NOPE` | HTTP 404; `No such loan.` |
| `POST /payments/L3` | HTTP 502; `payment gateway unavailable` because the configured local test port refused the connection |
| `POST /payments/NOPE` | HTTP 404; `no such loan` |
| `GET /about` | HTTP 200; returned the Lending Library about page |
| `POST /loans` with `member=eval&isbn=9780000000000` | HTTP 201; created L4 |
| `POST /loans/L4/return` | HTTP 200; returned L4 and set its returned date |

The process was terminated after the probes. The gateway override avoided contacting an external host. Jersey logged warnings that its registered resource classes were ignored as providers, but the listed routes responded as shown. The Maven-generated `legacy/target/` output was removed after the run; no source files were changed.

The application builds and runs from its own script, and its HTTP interface was exercised, so the default characterization tier is A.
