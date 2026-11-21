# Run journal: LC-ACCEPT

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T05:10:21+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |

Acceptance evidence was recorded for [Actions run 42752283868](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42752283868), attempt 1, commit `70fef8e7bc822092770b04b1bf9b5288e04d8bb6`. The run was not rerun in this session; the verified archive is `.migration/evidence/acceptance-runs/42752283868-1.json`.
| 2026-11-10T03:59:00+00:00 | mutation_full-0 | 0 | 102.52 | `bash -c 'python .migration/harness/tools/afs-mutation --all'` | `4510bb8211bb915d` |  | gate=mutation score=0.920 threshold=0.8 killed=126 survived=11 files=9 base=all |
| 2026-11-21T05:11:59+00:00 | validate | 1 | 1.13 | `python .migration/harness/tools/validate.py .migration` | `d6880ecfbfbd6fce` | 49 file(s) checked, 1 error(s) |  |
| 2026-11-21T05:12:14+00:00 | validate | 0 | 1.15 | `python .migration/harness/tools/validate.py .migration` | `2f118c59d9d07eef` |  |  |
