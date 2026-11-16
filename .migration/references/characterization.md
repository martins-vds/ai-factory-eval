# Source characterization — SY-01

## Pin and tier

- Source: `martins-vds/ai-factory-synthetic-target`, commit
  `563c316ed51462b08fd6e58f3781a3c8b2890453`, subdirectory `legacy/`.
- Tier: **A**. The previously recorded live run packaged and started the full source app, and
  HTTP probes exercised its externally visible routes. This records the existing evidence; no
  source build or probe was rerun for this update.
- The intake pin is authoritative. The separate `.source` checkout SHA recorded in the earlier
  handoff is not substituted for it and does not invalidate this characterization.
- Evidence source: `.migration/handoffs/SY-01.md`, previous session's command/output record.

## Recorded commands and observations

1. `PORT=18080 timeout 45s bash legacy/run.sh`
   - Maven packaging succeeded, Hibernate/H2 initialized, and Grizzly started on port 18080.
   - The command ended with timeout exit 124 after 45 seconds because the server remained
     waiting for requests.
2. `PORT=18081 bash legacy/run.sh`
   - The application started on port 18081 for endpoint probes.
3. `for path in /about /loans /loans/not-found /fees/not-found; do printf '\\n### GET %s\\n' "$path"; curl -sS -i "http://127.0.0.1:18081$path"; done; printf '\\n### POST /loans\\n'; curl -sS -i -X POST -d 'member=Probe&isbn=9780000000000' http://127.0.0.1:18081/loans; printf '\\n### POST /payments/not-found\\n'; curl -sS -i -X POST http://127.0.0.1:18081/payments/not-found`
   - `GET /about` returned 200 HTML; `GET /loans` returned 200 with three seeded rows;
     `GET /loans/not-found` returned 404 `no such loan`; `GET /fees/not-found` returned 404
     HTML; `POST /loans` returned 201 with loan `L4`; `POST /payments/not-found` returned 404.
4. `printf '### GET /fees/L1\\n'; curl -sS -i http://127.0.0.1:18081/fees/L1; printf '\\n### POST /loans/L1/return\\n'; curl -sS -i -X POST http://127.0.0.1:18081/loans/L1/return; printf '\\n### GET /loans/L1 after return\\n'; curl -sS -i http://127.0.0.1:18081/loans/L1`
   - The fee request returned 200 with `$10.00`; return returned 200 with returned date
     `2026-11-16`; the subsequent loan lookup returned 200 with that returned date.

## Observed quirk and limits

- Startup logged Jersey warnings that registered resources were ignored, although the probed
  routes returned live responses. Preserve this as an observed quirk; it is not evidence that
  those routes are unavailable.
- The payment gateway was not called for an existing loan.
- This evidence covers only the requests listed above. It is not a full characterization suite.
  Source test inventory and source coverage/complexity measurements were not established in
  the evidence transferred here.
