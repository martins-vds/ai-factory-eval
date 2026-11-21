# Slice library-info — acceptance evidence

- Tickets: LL-04 (#65), verifier issues #104 and #113, LI-AUDIT (#122), LI-ACCEPT (#127)
- Acceptance run: [42938753426, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42938753426)
- Commit: `7d4b249e342a94e7176ebf3e1d370f81d7156b16`
- Archived result: `.migration/evidence/acceptance-runs/42938753426-1.json`
- Acceptance date: 2026-11-11

The archived result is for the specified commit and run attempt, and records `status: passed`. The Auditor's independent report confirms the source and target graphs, gate results, and archive; acceptance gates and mutation were not rerun for LI-ACCEPT. The acceptance journal rows are in `.migration/evidence/runs/LI-ACCEPT.md`.

## Acceptance results

| Gate | Command | Exit | Notes |
|---|---|---:|---|
| Runtime, harness integrity, services | `check_runtime.py`; `check_installed.py`; `afs-services check` | 0 | All passed. |
| Graph freshness | `check_graph_fresh.py --require source,target` | 0 | Required source and target graphs were fresh. |
| Source graph | `graph_gate.py --side source --require-graph` | 0 | 8 entry points; 6 reaching data. |
| Target graph | `graph_gate.py --side target --require-graph --enforce-ownership` | 0 | 27 entry points; 18 reaching data. Both About routes have no data path. |
| Build | `python -m compileall -q src`; `python manage.py check` | 0 | Both passed. |
| Idiom | `ruff check src config manage.py tests`; `ruff format --check src config manage.py tests` | 0 | Both passed. |
| Tests | `pytest -q` | 0 | Full suite passed. |
| CRAP | `pytest -q --cov=src --cov-report=lcov:.migration/runs/crap.lcov`; `lizard --csv src`; `crap.py ... --max 30` | 0 | Maximum 7.0; threshold 30. |
| Full mutation | `python .migration/harness/tools/afs-mutation --all` | 0 | Score 0.976; threshold 0.8; 244 killed, 6 survived, base `all`. |

## Characterization and verification

`about.page` has tier-A differential characterization. The source golden specifies `GET /about` as HTTP 200, `text/html`, and exact static HTML; the target endpoint test matches the status, content type, and body. The separate target-only `GET /ui/about/` is the approved reading-room page, covering the library description, opening hours, 14-day lending term, contact link, and Loans navigation.

LL-04 was first verified as blocked in issue #104 / PR #105 because of the unrelated loan-browser suite failure and mutation collection failure. Its re-verification in issue #113 / PR #115 passed build, behavior, idiom, CRAP (7.0), changed-code mutation (1.000), and regression. LI-AUDIT in issue #122 / PR #125 returned `complete`: one capability checked, no gaps, and no graph inconsistencies. See `.migration/evidence/library-info/report.md` and `.migration/returns/LI-AUDIT.afs-auditor.yaml`.

## Capability coverage and ledger

| Capability | Target components | Status | Verification | Characterization | Evidence |
|---|---|---|---|---|---|
| `about.page` | Routes, About views, legacy and reading-room templates | `migrated` | `differential` | Tier A | HTTP golden comparison; HTTP and browser behavior tests; `.migration/evidence/runs/LL-04.md` |

`.migration/ledger/about.page.yaml` is the only library-info ledger entry. Its current status is supported by the differential HTTP golden comparison and executable HTTP/browser tests. The review-only drill in PR #119 did not merge and does not change the `differential` verification on `main`. The six full-run mutation survivors affect other slices; none touches library-info. LL-04's changed-code mutation score was 1.000, with 8 killed and no survivors.

The approved quirk rulings #39–#43 concern other capabilities and do not affect the About page boundary.

## Human side-by-side check

Human check is **requested**, not signed off. Compare the legacy `/about` page against the target `/about` page for the About text and library details (opening hours, lending policy, and contact information). Then compare those same facts on the target `/ui/about/` page with the legacy page, and compare the modernized `/ui/about/` layout with the plan's `reading-room` decision and approved Tailwind/daisyUI/htmx direction (decision map #38 and prototype #50). The legacy source has no matching modern UI route; this check does not claim visual equivalence to a source UI.
