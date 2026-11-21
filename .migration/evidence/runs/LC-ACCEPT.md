# Run journal: LC-ACCEPT

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T05:57:38+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-10T03:59:00+00:00 | mutation_full-0 | 0 | 102.52 | `bash -c 'python .migration/harness/tools/afs-mutation --all'` | `4510bb8211bb915d` |  | gate=mutation score=0.920 threshold=0.8 killed=126 survived=11 files=9 base=all |
| 2026-11-21T05:59:07+00:00 | validate | 1 | 0.78 | `python .migration/harness/tools/validate.py .migration` | `3df5a8a19d67243b` | 49 file(s) checked, 1 error(s) |  |
| 2026-11-21T05:59:25+00:00 | finish-check | 1 | 18.53 | `python .migration/harness/tools/afs-finish-check --ticket LC-ACCEPT --role afs-program-orchestrator` | `50603da91fb84a95` | [mechanical] CI's validate.py will fail on this: .migration/returns/LC-ACCEPT.afs-program-orchestrator.yaml: acceptance. | gate=finish-check ticket=LC-ACCEPT role=afs-program-orchestrator findings=1 |
| 2026-11-21T05:59:39+00:00 | validate | 1 | 0.76 | `python .migration/harness/tools/validate.py .migration` | `3df5a8a19d67243b` | 49 file(s) checked, 1 error(s) |  |
| 2026-11-21T05:59:57+00:00 | finish-check | 1 | 18.4 | `python .migration/harness/tools/afs-finish-check --ticket LC-ACCEPT --role afs-program-orchestrator` | `50603da91fb84a95` | [mechanical] CI's validate.py will fail on this: .migration/returns/LC-ACCEPT.afs-program-orchestrator.yaml: acceptance. | gate=finish-check ticket=LC-ACCEPT role=afs-program-orchestrator findings=1 |
| 2026-11-21T06:00:13+00:00 | validate | 0 | 0.77 | `python .migration/harness/tools/validate.py .migration` | `2f118c59d9d07eef` |  |  |
| 2026-11-21T06:00:31+00:00 | finish-check | 0 | 18.81 | `python .migration/harness/tools/afs-finish-check --ticket LC-ACCEPT --role afs-program-orchestrator` | `cba677bb03b44d19` |  | gate=finish-check ticket=LC-ACCEPT role=afs-program-orchestrator findings=0 |
