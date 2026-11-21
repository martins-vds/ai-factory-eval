# Characterization evidence

## Source and environment

- Source: `martins-vds/ai-factory-synthetic-target`, commit `563c316ed51462b08fd6e58f3781a3c8b2890453`, path `legacy`.
- Verified the pinned and checked-out `legacy/` trees are identical: both resolve to tree `1e683e0091beb079121c2ab6d223573ae29186ae`.
- Runtime: OpenJDK 17.0.21, Maven 3.10.0.
- Source stack from `legacy/pom.xml`: Java 17, Maven, Jersey/JAX-RS 3.1.5, Hibernate ORM 6.4.4.Final, H2 2.2.224. Source files are ASCII (UTF-8-compatible).

## Commands and observations

The initial invocation `./run.sh` from the repository root failed with exit 127 because the script is in `legacy/`. The corrected run was:

```sh
cd /home/runner/work/ai-factory-synthetic-target/ai-factory-synthetic-target/legacy
./run.sh
```

`run.sh` ran `mvn -q -B package -DskipTests` successfully, then started `lib.App` on port 8080. Hibernate connected to the in-memory H2 database and Grizzly reported `Lending Library listening on 8080`. Jersey logged warnings that its registered resource classes were ignored as providers, but the probes below all reached the expected endpoints.

With the server running, these commands returned:

| Command | Result |
|---|---|
| `curl -i --max-time 5 http://localhost:8080/loans` | HTTP 200; three seeded loan rows (`L1`, `L2`, `L3`) in semicolon-separated form. |
| `curl -i --max-time 5 http://localhost:8080/fees/L3` | HTTP 200; `Fee: $4.75` and `19 day(s) late`. |
| `curl -i --max-time 5 -X POST http://localhost:8080/payments/L3` | HTTP 502; body `payment gateway unavailable`. |
| `curl -i --max-time 5 http://localhost:8080/about` | HTTP 200; HTML title and heading identify the Lending Library. |
| `curl -i --max-time 5 -X POST -d member=dee -d isbn=123 http://localhost:8080/loans` | HTTP 201; body `L4;dee;123;2026-11-08;2026-11-22;`. |

These observations establish characterization tier A: the pinned source can be built, run, and exercised through its HTTP interface. No source files were changed.

## SY-05 expanded tier-A characterization

The existing harness was extended to exercise the ordinary endpoint flows, their reachable error and boundary cases, browser headings, and a process restart. The run on 2026-11-21 matched the recorded source predictions for all 18 HTTP scenarios and both browser checks. `python .migration/characterization/source/characterize.py` verified the goldens; the durable run journal is `.migration/evidence/runs/SY-05.md`.

| Input | Prediction from source | Observed |
|---|---|---|
| `GET /about` and browser navigation | Return the static About HTML with HTTP 200 and its library heading. | HTTP 200; page title and heading identify the Lending Library. |
| `GET /loans` | Return L1–L3 in id order, semicolon-delimited with due/return dates and a final newline. | Exact three seeded records in the predicted order and format. |
| `GET /loans/L1` | Return the matching record with HTTP 200. | HTTP 200 with L1's line. |
| `POST /loans` (`member=dee`, `isbn=123`) | Create L4 with today's lent date, a 14-day due date, and HTTP 201. | HTTP 201 with `L4;dee;123;2026-11-21;2026-12-05;`. |
| `POST /loans/L1/return` | Return L1 with today's returned date and HTTP 200. | HTTP 200 with L1's returned date set to `2026-11-21`. |
| `GET /fees/L3` | Use its returned date: 19 days late, $4.75. | HTTP 200 HTML displayed 19 days late and `$4.75`. |
| `POST /payments/L3` | The default unavailable gateway is mapped to HTTP 502. | HTTP 502, `payment gateway unavailable`. |
| Unknown loan GET, fee, payment, and return requests | Return HTTP 404 with the endpoint's `no such loan`/fee-not-found body. | All four requests returned HTTP 404 with the expected bodies. |
| `POST /loans` with missing ISBN | Return HTTP 400 because a required form value is absent. | HTTP 400, `member and isbn are required`. |
| `POST /loans` with empty member and ISBN | The source checks only for null values, so empty strings pass validation. | HTTP 201 created `L5;;;2026-11-21;2026-12-05;`; this is tracked in `.migration/quirks/blank-loan-fields.md`. |
| `GET /fees/L1` | L1 is overdue beyond the $10 cap. | HTTP 200 showed 309 days late and `$10.00`. |
| `GET /fees/L2` | Its returned date precedes its due date, so lateness is clamped to zero. | HTTP 200 showed 0 days late and `$0.00`. |
| `POST /loans/L2/return`, then `GET /loans/L2` | `markReturned` assigns today's date even when a return date already exists. | The seeded `2026-01-20` date was overwritten with `2026-11-21` and persisted; see `.migration/quirks/repeated-loan-return.md`. |
| Restart after creating/returning loans | The in-memory database and drop-and-create schema reload the three seed records. | L4 and L5 and the changed L1/L2 return dates disappeared; L1–L3 returned to seed values. See `.migration/quirks/restart-data-loss.md`. |

The pinned legacy tree contains no test source directory or legacy test files. The payment success response and a deliberately interrupted payment request were not exercised: the default gateway is unavailable, and no stand-in was used. The reporting document is a tier-C, specification-only request because it states the former product's code/runtime are unavailable and the source graph has no report endpoint.
