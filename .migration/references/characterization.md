# Legacy characterization evidence

Source: `martins-vds/ai-factory-synthetic-target` at
`563c316ed51462b08fd6e58f3781a3c8b2890453`, path `legacy`.
The pinned tree hash was `1e683e0091beb079121c2ab6d223573ae29186ae`, equal to the checked-out
`HEAD:legacy` tree. The original source was left unchanged; build artifacts were created only in
`/tmp/sy01-legacy.am0xFD/legacy`.

## Stack detection

- Java 17 and Maven (`legacy/run.sh`, `legacy/pom.xml`); Maven compiler release 17.
- Jersey 3.1.5 / JAX-RS 3.1 on Grizzly; Hibernate ORM 6.4.4.Final / JPA and H2 2.2.224.
- UTF-8 source encoding, declared in `legacy/pom.xml`.
- The target stacks are the operator-provided Python 3.13, Django 5, Django templates, and PostgreSQL 17.

## Build and launch

Environment: OpenJDK `17.0.21`, Maven `3.10.1`.

Ran:

```bash
tmp=$(mktemp -d /tmp/sy01-legacy.XXXXXX) &&
cp -a /home/runner/work/ai-factory-eval/ai-factory-eval/legacy "$tmp/legacy" &&
cd "$tmp/legacy" &&
PORT=18080 ./run.sh
```

`run.sh` ran `mvn -q -B package -DskipTests`, then started `lib.App`; output included
`Lending Library listening on 18080`. Hibernate created the in-memory H2 database and loaded its
three seed loans. Jersey logged resource-registration warnings, but all routes below responded.
The source contains no test-source directory; the script explicitly skips Maven tests.

For the payment success probe, stopped that process and relaunched the same temporary copy with
`PAYMENT_GATEWAY_URL=http://127.0.0.1:18081 PORT=18080 ./run.sh`. The loopback gateway was started with:

```bash
python -c 'from http.server import BaseHTTPRequestHandler,HTTPServer; exec("class H(BaseHTTPRequestHandler):\n def do_POST(self):\n  self.send_response(200); self.end_headers(); self.wfile.write(b\"charged\\n\")\n def log_message(self,*a): pass"); HTTPServer(("127.0.0.1",18081),H).serve_forever()'
```

It returned status 200 and body `charged\n`; no external gateway was contacted.

## HTTP probes

All requests used `curl` against `http://127.0.0.1:18080`; dates below reflect the run on
2026-11-21.

| Exact command | Observed result |
|---|---|
| `curl -sS -i http://127.0.0.1:18080/loans` | 200 `text/plain`; three semicolon-separated records, L1–L3, ordered by id. |
| `curl -sS -i http://127.0.0.1:18080/loans/L2` | 200; `L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20`. |
| `curl -sS -i http://127.0.0.1:18080/loans/missing` | 404; `no such loan\n`. |
| `curl -sS -i -X POST http://127.0.0.1:18080/loans` | 500 Grizzly error page because no body or form content type was supplied. |
| `curl -sS -i -X POST -H 'Content-Type: application/x-www-form-urlencoded' --data '' http://127.0.0.1:18080/loans` | 400; `member and isbn are required\n`. |
| `curl -sS -i -X POST -H 'Content-Type: application/x-www-form-urlencoded' --data 'member=only' http://127.0.0.1:18080/loans` and the same command with `--data 'isbn=only'` | Both 400; `member and isbn are required\n`. |
| `curl -sS -i -X POST -d 'member=zoe&isbn=123' http://127.0.0.1:18080/loans` | 201; `L4;zoe;123;2026-11-21;2026-12-05;`. |
| `curl -sS -i -X POST http://127.0.0.1:18080/loans/L3/return` | 200; L3 returned on `2026-11-21`. |
| `curl -sS -i http://127.0.0.1:18080/fees/L3` | 200 HTML; 341 days late and fee capped at `$10.00`. |
| `curl -sS -i http://127.0.0.1:18080/fees/missing` | 404 HTML; `<p>No such loan.</p>`. |
| `curl -sS -i -X POST http://127.0.0.1:18080/payments/missing` | 404; `no such loan\n`. |
| `curl -sS -i -X POST http://127.0.0.1:18080/payments/L1` | 200; `charged\n` from the local scratch gateway. |
| `curl -sS -i http://127.0.0.1:18080/about` | 200 HTML, 293 bytes; title “About the Lending Library”, Monday–Saturday hours, 14-day policy, and contact address. |

This is tier A: the pinned source builds and runs, and its HTTP boundary was exercised directly.
