# Legacy characterization — SY-01

## Stack and encoding

- Java 17, Maven, Jersey/JAX-RS 3.1.5 on Grizzly, JPA with Hibernate 6.4.4, H2 2.2.224.
- UI is static HTML plus HTML responses from JAX-RS resources; no JavaScript UI framework was found.
- `FinePayments` calls `PAYMENT_GATEWAY_URL` over HTTP. Its default is a `.invalid` URL.
- `legacy/pom.xml` declares UTF-8. H2 is an in-memory database with seed rows loaded at startup.
- The target stack supplied for intake is Python 3.13, Django 5, Django templates, and PostgreSQL 17.

## Tier and evidence

Tier A: the legacy app built and started locally with its real Java/H2 runtime.

Commands:

1. `./legacy/run.sh` — `mvn -q -B package -DskipTests` completed; Hibernate initialized H2 and Grizzly started on `0.0.0.0:8080`. The Java process stayed in the foreground as expected and was stopped after endpoint probes.
2. `curl --silent --show-error --max-time 4 -i http://127.0.0.1:8080/...` for GET probes and `curl ... -X POST` for form/action probes — all reported below.

Observed responses (2026-11-16 UTC; seeded dates are fixed):

| Request | Result |
|---|---|
| `GET /` | 404 |
| `GET /about` | 200, HTML about page |
| `GET /loans` | 200, three semicolon-separated seeded rows (`L1`–`L3`) |
| `GET /loans/L1` | 200, one semicolon-separated loan row |
| `GET /loans/demo` | 404, `no such loan` |
| `GET /fees/demo` | 404, `<p>No such loan.</p>` |
| `GET /fees/L2` | 200, fee `$0.00` |
| `GET /fees/L3` | 200, 19 days late, fee `$4.75` |
| `POST /loans` with no form | **500** Grizzly `Request failed.` (the source method appears to intend 400 when fields are absent) |
| `POST /loans` with `member=SY01&isbn=9780000000001` | 201, new loan `L4`, due 2026-11-30 |
| `POST /loans/L4/return` | 200, returned date 2026-11-16 |
| `POST /payments/no-such-loan` | 404 before contacting the payment gateway |

No valid-loan payment request was sent, to avoid a call to the external gateway. Writes were confined to the ephemeral in-memory H2 database.

## Source pin/setup caveat

The supplied SHA exists in the current repository object database, and the tracked `legacy/` files match its `legacy/` tree. The separately mounted, read-only `.source/` checkout does **not** satisfy the pin check: its HEAD is `ffa05e628142843a5afdbf742da1c58ac05304f8`, not `563c316ed51462b08fd6e58f3781a3c8b2890453`, and its recorded remote is `martins-vds/ai-factory-eval`, not the source repository in `.migration/source.lock`. The requested source content was characterized from the matching tracked `legacy/` tree; the dispatcher must restore the correct read-only `.source/` checkout before installation or later phases.

## Existing source tests / warnings

No `src/test` tree or JUnit dependency is present. The existing `.github/workflows/legacy-smoke.yml` defines endpoint smoke probes. Startup printed Jersey warnings that the four resource instances were ignored as providers, although the probed endpoints were reachable and returned the results above. Preserve both the missing-form 500 and startup warnings as observed behavior until the human decides otherwise.
