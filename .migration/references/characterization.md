# Legacy characterization

## Environment and provenance

- Tier A: the source application built, started, and responded through its HTTP interface.
- Pinned source: `martins-vds/ai-factory-synthetic-target`, commit `563c316ed51462b08fd6e58f3781a3c8b2890453`, path `legacy`.
- Compared the local `legacy/` files and directory object IDs with the pinned GitHub tree; the contents match. The legacy source was not modified.
- All 14 tracked legacy files decode as UTF-8; the profile records `UTF-8`.
- Runtime: OpenJDK `17.0.21`; Maven `3.10.0`.
- Build and start command, from the repository root: `PORT=18080 ./legacy/run.sh`.
- No legacy test sources are present under `legacy/src/test`.

## HTTP observations

After startup, `curl` probes against `http://127.0.0.1:18080` observed:

```sh
curl -sf http://127.0.0.1:18080/loans
curl -s -o /tmp/sy01-loans.txt -w '%{http_code}' http://127.0.0.1:18080/loans
curl -s -o /tmp/sy01-fee.txt -w '%{http_code}' http://127.0.0.1:18080/fees/L3
curl -s -o /tmp/sy01-payment.txt -w '%{http_code}' -X POST http://127.0.0.1:18080/payments/L3
curl -s -o /tmp/sy01-about.txt -w '%{http_code}' http://127.0.0.1:18080/about
curl -s -o /tmp/sy01-post.txt -w '%{http_code}' -X POST -d member=dee -d isbn=123 http://127.0.0.1:18080/loans
curl -s -o /tmp/sy01-missing.txt -w '%{http_code}' http://127.0.0.1:18080/loans/unknown
```

Observed statuses and response bodies:

- `GET /loans` → 200:

  ```text
  L1;ana;9780134685991;2026-01-02;2026-01-16;
  L2;bo;9780596007126;2026-01-10;2026-01-24;2026-01-20
  L3;cy;9781617294945;2025-12-01;2025-12-15;2026-01-03
  ```

- `GET /fees/L3` → 200:

  ```html
  <h1>Late fee for L3</h1><p>Due 2025-12-15, 19 day(s) late.</p><p class="fee">Fee: $4.75</p>
  ```

- `POST /payments/L3` → 502:

  ```text
  payment gateway unavailable
  ```

- `GET /about` → 200:

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

- `POST /loans` with `member=dee` and `isbn=123` → 201:

  ```text
  L4;dee;123;2026-11-15;2026-11-29;
  ```

- `GET /loans/unknown` → 404:

  ```text
  no such loan
  ```

These are observed outputs, not predictions. The tier-A characterization tier is based on the running app and externally visible HTTP responses.
