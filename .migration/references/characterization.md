# Characterization evidence

## Source and environment

- Source: `martins-vds/ai-factory-synthetic-target`, commit `563c316ed51462b08fd6e58f3781a3c8b2890453`, path `legacy`.
- The pinned and checked-out `legacy/` trees both resolve to `1e683e0091beb079121c2ab6d223573ae29186ae`.
- Runtime: OpenJDK 17.0.21 and Maven (the script's `mvn` invocation succeeded).
- Source stack from `legacy/pom.xml`: Java 17, Maven, Jersey/JAX-RS 3.1.5, Hibernate ORM 6.4.4.Final, H2 2.2.224. The source files are UTF-8-compatible.

## Commands and observations

To keep generated Maven output out of the read-only source tree, an inline Python 3.13 runner copied `legacy/` to `/tmp/sy01-characterization-1xrjoaq_/legacy`, launched `bash run.sh` from that directory with `PORT=18081`, and stopped the child process after probing. `run.sh` ran `mvn -q -B package -DskipTests` successfully, then started `lib.App`; Hibernate connected to `jdbc:h2:mem:library;DB_CLOSE_DELAY=-1` and the app printed `Lending Library listening on 18081`. Jersey logged warnings that its registered resources were ignored as providers, although the endpoints below responded.

The runner waited for `GET /loans` to succeed, then made the following Python `urllib.request` calls:

| Request | Status and response body |
|---|---|
| `GET /loans` | HTTP 200; three seeded semicolon-separated records: `L1;ana;9780134685991;2026-01-02;2026-01-16;`, `L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20`, and `L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03`. |
| `GET /loans/L1` | HTTP 200; `L1;ana;9780134685991;2026-01-02;2026-01-16;` |
| `GET /loans/missing` | HTTP 404; `no such loan` |
| `POST /loans` with an empty body | HTTP 400; `member and isbn are required` |
| `POST /loans` with `member=eval&isbn=9780000000000` | HTTP 201; `L4;eval;9780000000000;2026-11-19;2026-12-03;` |
| `GET /fees/L1` | HTTP 200; `<h1>Late fee for L1</h1><p>Due 2026-01-16, 307 day(s) late.</p><p class="fee">Fee: $10.00</p>` |
| `GET /fees/missing` | HTTP 404; `<p>No such loan.</p>` |
| `POST /loans/L4/return` with an empty body | HTTP 200; `L4;eval;9780000000000;2026-11-19;2026-12-03;2026-11-19` |
| `POST /loans/missing/return` with an empty body | HTTP 404; `no such loan` |
| `POST /payments/missing` with an empty body | HTTP 404; `no such loan` |
| `GET /about` | HTTP 200; `<!doctype html>` with title and heading `About the Lending Library`; body text: `Open Monday to Saturday, 9:00 to 18:00. Books are lent for 14 days.` and `Contact: desk@lending-library.invalid`. |
| Final `GET /loans` | HTTP 200; the three seed records plus the created and returned L4 record. |

These observations establish characterization tier A: the pinned source builds, runs, and responds through its HTTP interface. No files under `legacy/` were changed.
