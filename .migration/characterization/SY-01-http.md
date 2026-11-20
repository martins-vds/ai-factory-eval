# SY-01 legacy characterization

## Build and run

From the repository root, ran `./legacy/run.sh`. Maven packaging exited successfully; the process logged `Lending Library listening on 8080` and `Started listener bound to [0.0.0.0:8080]`. It used OpenJDK 17.0.21, Maven 3.10.0, Jersey 3.1.5, Hibernate 6.4.4.Final, H2 2.2.224, and an in-memory H2 database. The source tree at `legacy/` matched the `legacy/` tree at pinned commit `563c316ed51462b08fd6e58f3781a3c8b2890453`.

## HTTP probes

All requests used `curl -sS -i` against `http://127.0.0.1:8080`; dates below are the observed server date, 2026-11-20.

| Request | Result |
| --- | --- |
| `GET /` | `404 Not Found`, empty body. |
| `GET /about` | `200 OK`, `text/html`; full response body shown below. |
| `GET /loans` | `200 OK`, `text/plain`; body: `L1;ana;9780134685991;2026-01-02;2026-01-16;`, `L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20`, and `L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03`, each on its own line. |
| `GET /loans/L1` | `200 OK`; body `L1;ana;9780134685991;2026-01-02;2026-01-16;`. |
| `GET /loans/missing` | `404 Not Found`; body `no such loan`. |
| `POST /loans` with no form body | `500 Request failed.`, `text/html;charset=ISO-8859-1`, 1031-byte Grizzly 4.0.1 error page. |
| `POST /loans` with only `member=eval` | `400 Bad Request`; body `member and isbn are required`. |
| `POST /loans` with only `isbn=9780000000000` | `400 Bad Request`; body `member and isbn are required`. |
| `POST /loans` with `member=eval&isbn=9780000000000` | `201 Created`; body `L4;eval;9780000000000;2026-11-20;2026-12-04;`. |
| `POST /loans/missing/return` | `404 Not Found`; body `no such loan`. |
| `POST /loans/L2/return` | `200 OK`; body `L2;bo;9780596007126;2026-01-10;2026-01-24;2026-11-20`. |
| `GET /fees/L1` | `200 OK`, `text/html`; body `<h1>Late fee for L1</h1><p>Due 2026-01-16, 308 day(s) late.</p><p class="fee">Fee: $10.00</p>`. |
| `GET /fees/missing` | `404 Not Found`, `text/html`; body `<p>No such loan.</p>`. |
| `POST /payments/missing` | `404 Not Found`; body `no such loan`; the missing-loan response returned before contacting the payment gateway. |

The valid-loan payment path was not called because the default gateway URL is a reserved `.invalid` host; no external payment service was contacted.

The exact `GET /about` body was:

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
