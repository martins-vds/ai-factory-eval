# Legacy characterization

## Environment and tier

**Tier A.** The pinned Java 17 application built and ran from `legacy/run.sh` in this environment. I
started it with:

```sh
cd /home/runner/work/ai-factory-eval/ai-factory-eval/legacy && ./run.sh
```

The script ran `mvn -q -B package -DskipTests` and started `lib.App` on its default port, 8080. I
confirmed the service was available by probing its HTTP endpoints. The server was stopped after the
probes; no files under `legacy/` were changed.

## Observed requests and responses

The initial `GET /loans` returned the seeded rows:

```text
L1;ana;9780134685991;2026-01-02;2026-01-16;
L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20
L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03
```

Other probes used `curl -sS -i`:

| Request | Observed result |
|---|---|
| `GET /loans/L3` | 200 text/plain; `L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03` |
| `GET /fees/L3` | 200 text/html; due 2025-12-15, 19 days late, fee `$4.75` |
| `POST /payments/L3` | 502 text/plain; `payment gateway unavailable` |
| `GET /about` | 200 text/html; page title and heading “About the Lending Library”, hours, 14-day loan policy, and contact |
| `POST /loans` with `-d member=dee -d isbn=123` | 201 text/plain; `L4;dee;123;2026-11-15;2026-11-29;` |
| `POST /loans/L4/return` | 200 text/plain; `L4;dee;123;2026-11-15;2026-11-29;2026-11-15` |
| `GET /loans/unknown` | 404 text/plain; `no such loan` |
| `GET /fees/unknown` | 404 text/html; `<p>No such loan.</p>` |
| `POST /payments/unknown` | 404 text/plain; `no such loan` |
| `POST /loans` with no body or form content type | 500 Grizzly “Request failed.”; this was not a form-encoded missing-field probe |

The fee and new-loan dates reflect the environment date, 2026-11-15. The default payment gateway
was unreachable, producing the observed 502 response.

## Source inventory

The tracked source is Java 17, built by Maven, with JAX-RS resources on Grizzly and Hibernate/JPA on
H2. The repository has no tracked Java test sources or source coverage configuration. The source also
contains `legacy/docs/reports-spec.md`, a specification for a reporting module whose code and runtime
are no longer present.
