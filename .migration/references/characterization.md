# Legacy characterization

**Source:** `martins-vds/ai-factory-synthetic-target`, commit
`563c316ed51462b08fd6e58f3781a3c8b2890453`, path `legacy/`.
**Tier:** A — a running legacy environment was available.

## Run

From the repository root, ran:

```bash
PORT=18080 ./legacy/run.sh
```

The script completed `mvn -q -B package -DskipTests`, started the app, and printed
`Lending Library listening on 18080`. It initialized its in-memory H2 database from the seed data.
The server log also included Jersey provider-registration warnings; the routes below still responded.

The exact probe loop was:

```bash
set +e
base=http://127.0.0.1:18080
for spec in 'GET /loans' 'GET /loans/L1' 'GET /loans/missing' 'GET /fees/L3' 'GET /fees/missing' 'POST /payments/L3' 'GET /about'; do
  method=${spec%% *}; path=${spec#* }
  curl -sS -i -X "$method" "$base$path" | sed -n '1,16p'
done
curl -sS -i -X POST -d 'member=dee' -d 'isbn=123' "$base/loans" | sed -n '1,20p'
curl -sS -i -X POST -d 'member=dee' "$base/loans" | sed -n '1,16p'
curl -sS -i -X POST "$base/loans/L1/return" | sed -n '1,18p'
curl -sS -i -X POST "$base/loans/no-such/return" | sed -n '1,16p'
```

Status, content type, and body below are the observed responses on 2026-11-16.

### Loans

`GET /loans` returned `200 OK`, `Content-Type: text/plain`:

```text
L1;ana;9780134685991;2026-01-02;2026-01-16;
L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20
L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03
```

`GET /loans/L1` returned `200 OK`, `Content-Type: text/plain`:

```text
L1;ana;9780134685991;2026-01-02;2026-01-16;
```

`GET /loans/missing` returned `404 Not Found`, `Content-Type: text/plain`:

```text
no such loan
```

`curl -sS -i -X POST -d 'member=dee' -d 'isbn=123' http://127.0.0.1:18080/loans`
returned `201 Created`, `Content-Type: text/plain`:

```text
L4;dee;123;2026-11-16;2026-11-30;
```

`curl -sS -i -X POST -d 'member=dee' http://127.0.0.1:18080/loans` returned
`400 Bad Request`, `Content-Type: text/plain`:

```text
member and isbn are required
```

`curl -sS -i -X POST http://127.0.0.1:18080/loans/L1/return` returned `200 OK`,
`Content-Type: text/plain`:

```text
L1;ana;9780134685991;2026-01-02;2026-01-16;2026-11-16
```

`curl -sS -i -X POST http://127.0.0.1:18080/loans/no-such/return` returned
`404 Not Found`, `Content-Type: text/plain`:

```text
no such loan
```

### Fees, payments, and about page

`GET /fees/L3` returned `200 OK`, `Content-Type: text/html`:

```html
<h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p><p class="fee">Fee: $4.75</p>
```

`GET /fees/missing` returned `404 Not Found`, `Content-Type: text/html`:

```html
<p>No such loan.</p>
```

`POST /payments/L3` returned `502 Bad Gateway`, `Content-Type: text/plain`:

```text
payment gateway unavailable
```

`GET /about` returned `200 OK`, `Content-Type: text/html`:

```html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>About the Lending Library</title></head>
<body>
  <h1>About the Lending Library</h1>
  <p>Open Monday to Saturday, 9:00 to 18:00. Books are lent for 14 days.</p>
  <p>Contact: desk@lending-library.invalid</p>
</body>
</html>
```

The create and return requests changed only the running in-memory database; the server was stopped
after probing. The repository has an existing workflow smoke test, but no repeatable
characterization test harness, so the capability checklist records that gap separately from the
tier-A run evidence.
