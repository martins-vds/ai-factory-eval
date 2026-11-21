# Run journal: LF-ACCEPT

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T06:50:36+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-21T06:51:28+00:00 | acceptance-fetch | 2 | 0.19 | `python .migration/harness/tools/afs-acceptance fetch --run-id 42912984554 --attempt 1 --dest .migration/runs/acceptance-42912984554-1` | `a2bf2c6e8b61bb68` |  |  |
| 2026-11-21T06:52:38+00:00 | acceptance-verify | 2 | 0.05 | `python .migration/harness/tools/afs-acceptance verify .migration/runs/acceptance-42912984554-1 --run-id 42912984554 --attempt 1 --commit 8f9a11640eef9801378f3db53a76903363c5e5b5` | `1d432f27f2d34ce2` |  |  |
