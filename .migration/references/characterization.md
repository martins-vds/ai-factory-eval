# Legacy characterization

Source: `martins-vds/ai-factory-synthetic-target@563c316ed51462b08fd6e58f3781a3c8b2890453`, path `legacy`.
The local `legacy/` tree matches that revision.

## Run

From the repository root, ran:

```sh
./legacy/run.sh
```

The Maven package completed and the app started on port 8080. The output included Hibernate/H2 initialization
and `Lending Library listening on 8080`. Startup also logged warnings that the registered resource instances
were ignored; the endpoint requests below nevertheless succeeded.

Then ran this probe loop against `http://127.0.0.1:8080`:

```sh
for spec in 'GET /loans' 'GET /loans/L1' 'GET /loans/missing' 'POST /loans' \
  'POST /loans/L999/return' 'GET /fees/L3' 'GET /fees/missing' \
  'POST /payments/L3' 'GET /about'; do
  method=${spec%% *}; path=${spec#* }
  if [ "$method" = POST ] && [ "$path" = /loans ]; then
    result=$(curl -sS -w '\nHTTP %{http_code}' -X "$method" -d member=dee -d isbn=123 \
      "http://127.0.0.1:8080$path")
  else
    result=$(curl -sS -w '\nHTTP %{http_code}' -X "$method" \
      "http://127.0.0.1:8080$path")
  fi
  printf '\n--- %s %s ---\n%s\n' "$method" "$path" "$result"
done
```

## Observed behavior

| Request | Result |
| --- | --- |
| `GET /loans` | 200; lists seeded L1, L2, L3 as semicolon-separated records. |
| `GET /loans/L1` | 200; returns L1. |
| `GET /loans/missing` | 404; body `no such loan`. |
| `POST /loans` with `member=dee&isbn=123` | 201; creates L4 with today's date and a due date 14 days later. |
| `POST /loans/L999/return` | 404; body `no such loan`. |
| `GET /fees/L3` | 200 HTML; reports 19 days late and `Fee: $4.75`. |
| `GET /fees/missing` | 404; body `<p>No such loan.</p>`. |
| `POST /payments/L3` | 502; body `payment gateway unavailable`. |
| `GET /about` | 200 HTML; identifies the Lending Library, opening hours, 14-day lending period, and contact. |

The source is runnable in this environment and its HTTP behavior was observed directly; characterization tier A.
