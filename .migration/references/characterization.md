# Legacy characterization evidence

Source: `martins-vds/ai-factory-synthetic-target`, commit `563c316ed51462b08fd6e58f3781a3c8b2890453`, path `legacy/`.

## What was attempted

- Ran `./legacy/run.sh`. It entered `mvn -q -B package -DskipTests` and remained in Maven dependency resolution for 5m28s. No files appeared under `legacy/target`, and no server listened on port 8080. The process was stopped; the command did not return an exit code.
- The target clone is shallow and does not contain the pinned commit object. The remote pinned blobs for `legacy/run.sh`, `legacy/pom.xml`, `legacy/src/main/java/lib/App.java`, and `legacy/src/main/java/lib/LoanResource.java` match the corresponding local files exactly (Git blob hashes: `c0e7f49`, `f239b34`, `4e5a396`, and `825a464`).
- Tried the Tier B compile recipe on the independent `Loan` unit with `javac -d /tmp/sy01-javac -sourcepath legacy/src/main/java -implicit:class legacy/src/main/java/lib/Loan.java`. It exited 1 with 12 errors because `jakarta.persistence` is not present on the local classpath. `legacy/src/test/` is absent.
- Probed `GET /loans`, `GET /loans/L3`, `GET /about`, `GET /fees/L3`, `POST /payments/L3`, `POST /loans`, and `POST /loans/L3/return` against `127.0.0.1:8080`. Each curl returned exit 7, “Failed to connect,” because the app never started.

The endpoint probe loop ran these requests:

```bash
curl --max-time 2 -sS -i http://127.0.0.1:8080/loans
curl --max-time 2 -sS -i http://127.0.0.1:8080/loans/L3
curl --max-time 2 -sS -i http://127.0.0.1:8080/about
curl --max-time 2 -sS -i http://127.0.0.1:8080/fees/L3
curl --max-time 2 -sS -i -X POST http://127.0.0.1:8080/payments/L3
curl --max-time 2 -sS -i -X POST http://127.0.0.1:8080/loans
curl --max-time 2 -sS -i -X POST http://127.0.0.1:8080/loans/L3/return
```

Each printed `curl: (7) Failed to connect to 127.0.0.1 port 8080 after 0 ms: Couldn't connect to server`.

## Tier decision

Tier C: there is no running legacy environment in this session, the normal startup did not get past dependency resolution, and the isolated compile could not run without the JPA API. No endpoint response was observed. The Tier B attempt is recorded above; the dispatcher should re-run characterization if a usable Maven dependency cache or running environment becomes available.
