# Run journal: LI-ACCEPT

Written by `afs-run`, one row per gate run. Raw logs are not committed; the SHA-256 identifies the exact log. Result is the gate tool's own `AFS-RESULT` line.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---|---|---|---|---|---|
| 2026-11-21T05:07:51+00:00 | setup-probe | 0 | 0.0 | `true` | `e3b0c44298fc1c14` |  |  |
| 2026-11-11T01:36:13+00:00 | mutation_full-0 | 0 | 427.39 | `bash -c 'python .migration/harness/tools/afs-mutation --all'` | `unknown-archived-result` |  | gate=mutation score=0.976 threshold=0.8 killed=244 survived=6 files=17 base=all |

No acceptance build, test, CRAP, or mutation gates were rerun by this session. The result above records only the setup probe. Acceptance evidence was taken from the independently verified archive `.migration/evidence/acceptance-runs/42938753426-1.json` for run 42938753426, attempt 1, on commit `7d4b249e342a94e7176ebf3e1d370f81d7156b16`.
