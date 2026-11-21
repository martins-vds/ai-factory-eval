# Run journal: LF-ACCEPT

Review record for slice acceptance. The acceptance gates and mutation were not run in this session, as instructed; their evidence is the archived run and the Auditor's journal.

## Archived acceptance-run gate rows

These gate rows are reproduced from the acceptance evidence preserved in `.migration/evidence/runs/LF-AUDIT.md`. They belong to run 42912984554, attempt 1, and were not run again in this session.

| UTC | Gate | Exit | Seconds | Command | Log SHA-256 | First highlight | Result |
|---|---|---:|---:|---|---|---|---|
| 2026-11-10T22:20:42+00:00 | runtime | 0 | 0.08 | `/opt/hostedtoolcache/Python/3.13.18/x64/bin/python /home/runner/work/ai-factory-synthetic-target/ai-factory-synthetic-target/.migration/harness/tools/check_runtime.py` | `96436ba39c5ef665` |  |  |
| 2026-11-10T22:20:42+00:00 | harness-integrity | 0 | 0.08 | `/opt/hostedtoolcache/Python/3.13.18/x64/bin/python /home/runner/work/ai-factory-synthetic-target/ai-factory-synthetic-target/.migration/harness/tools/check_installed.py` | `dfd55d0883d0dcec` |  |  |
| 2026-11-10T22:20:42+00:00 | services | 0 | 0.23 | `/opt/hostedtoolcache/Python/3.13.18/x64/bin/python /home/runner/work/ai-factory-synthetic-target/ai-factory-synthetic-target/.migration/harness/tools/afs-services check` | `274667623a156426` |  |  |
| 2026-11-10T22:20:42+00:00 | graph-freshness | 0 | 0.08 | `/opt/hostedtoolcache/Python/3.13.18/x64/bin/python /home/runner/work/ai-factory-synthetic-target/ai-factory-synthetic-target/.migration/harness/tools/check_graph_fresh.py --require source,target` | `919151ce11bb145d` |  |  |
| 2026-11-10T22:20:42+00:00 | graph-source | 0 | 0.16 | `/opt/hostedtoolcache/Python/3.13.18/x64/bin/python /home/runner/work/ai-factory-synthetic-target/ai-factory-synthetic-target/.migration/harness/tools/graph_gate.py --side source --require-graph` | `dde05b7ab64808ca` |  | gate=graph side=source verdict=pass failures=0 entry_points=8 reaching_data=6 enriched_edges=67 |
| 2026-11-10T22:20:43+00:00 | graph-target | 0 | 0.2 | `/opt/hostedtoolcache/Python/3.13.18/x64/bin/python /home/runner/work/ai-factory-synthetic-target/ai-factory-synthetic-target/.migration/harness/tools/graph_gate.py --side target --require-graph --enforce-ownership` | `e337dc9638d13f20` |  | gate=graph side=target verdict=pass failures=0 entry_points=23 reaching_data=18 enriched_edges=148 |
| 2026-11-10T22:20:43+00:00 | build-0 | 0 | 0.05 | `bash -c 'python -m compileall -q src'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-10T22:20:43+00:00 | build-1 | 0 | 0.64 | `bash -c 'python manage.py check'` | `1e3e63f221bde888` |  |  |
| 2026-11-10T22:20:43+00:00 | idiom-0 | 0 | 0.01 | `bash -c 'ruff check src config manage.py tests'` | `82b3e6a6c090a576` |  |  |
| 2026-11-10T22:20:43+00:00 | idiom-1 | 0 | 0.01 | `bash -c 'ruff format --check src config manage.py tests'` | `2de9ddcc7788f957` |  |  |
| 2026-11-10T22:20:58+00:00 | tests-0 | 0 | 14.37 | `bash -c 'pytest -q'` | `cd3bad4d4305c078` |  |  |
| 2026-11-10T22:21:13+00:00 | crap-0 | 0 | 14.67 | `bash -c 'pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov'` | `df49fb3c4323369f` |  |  |
| 2026-11-10T22:21:13+00:00 | crap-1 | 0 | 0.08 | `bash -c 'lizard --csv src > .migration/runs/lizard.csv'` | `e3b0c44298fc1c14` |  |  |
| 2026-11-10T22:21:13+00:00 | crap-2 | 0 | 0.06 | `bash -c 'python .migration/harness/tools/crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30'` | `3e97bcd4c38fc824` |  | gate=crap max=7.0 threshold=30 over=0 methods=38 |
| 2026-11-10T22:28:25+00:00 | mutation_full-0 | 0 | 431.81 | `bash -c 'python .migration/harness/tools/afs-mutation --all'` | `0ced7daef681a111` |  | gate=mutation score=0.975 threshold=0.8 killed=236 survived=6 files=15 base=all |

| UTC | Action | Result |
|---|---|---|
| 2026-11-21T20:45:16Z | Inspect acceptance archive | Run 42912984554, attempt 1, reports `passed` on commit `8f9a11640eef9801378f3db53a76903363c5e5b5`; details are in `.migration/evidence/acceptance-runs/42912984554-1.json`. |
| 2026-11-21T20:45:16Z | Inspect audit and ledger | LF-AUDIT return is `complete`; the three fees entries are `migrated`. |
| 2026-11-21T20:45:16Z | Read live tracker issues | Read #62, #63, #90, #96, #114, #117 and the #40/#42 rulings. The provided descendant list accounts for #63, #90, #96, #114, and #117. |
| 2026-11-21T20:45:16Z | Preview ticket reconciliation | `reconcile_epic.py --repo martins-vds/ai-factory-synthetic-target --epic 62 --dry-run` could not read the sub-issues endpoint (`gh: HTTP 403`). No live tracker data was written; the reconciliation lists the supplied descendants and their directly read issue/PR evidence. |
| 2026-11-21T20:45:16Z | Validate existing migration state | `python .migration/harness/tools/validate.py .migration` exited 0; 49 files checked, 0 errors. |

The operator's legacy-versus-target side-by-side check is requested and remains outstanding. This session did not run build, tests, CRAP, or mutation.
