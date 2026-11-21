# Slice library-info — acceptance evidence

- Tickets: LL-04 (#65), LI-AUDIT (#122), LI-ACCEPT (#127) · Commit: `7d4b249e342a94e7176ebf3e1d370f81d7156b16` · Date: 2026-11-21
- Acceptance run: [42938753426, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42938753426), successful on `main`
- Verified archive: `.migration/evidence/acceptance-runs/42938753426-1.json` (`status: passed`, exact commit above)
- Independent audit: `.migration/evidence/library-info/report.md`; Auditor return `.migration/returns/LI-AUDIT.afs-auditor.yaml` is `complete`, with no gaps or graph inconsistencies.

## Gates

The coordinator did not rerun gates or mutation. The table records the independently verified acceptance run and its committed journal rows in `.migration/evidence/runs/LI-ACCEPT.md`.

| Gate | Command | Exit | Result |
|---|---|---:|---|
| Runtime | `check_runtime.py` | 0 | Passed |
| Harness integrity | `check_installed.py` | 0 | Passed |
| Services | `afs-services check` | 0 | Passed |
| Graph freshness | `check_graph_fresh.py --require source,target` | 0 | Passed |
| Source graph | `graph_gate.py --side source --require-graph` | 0 | Passed; 8 entry points, 6 reaching data |
| Target graph | `graph_gate.py --side target --require-graph --enforce-ownership` | 0 | Passed; 27 entry points, 18 reaching data |
| Build | `python -m compileall -q src`; `python manage.py check` | 0 | Both passed |
| Idiom | `ruff check src config manage.py tests`; `ruff format --check src config manage.py tests` | 0 | Both passed |
| Tests | `pytest -q` | 0 | Full suite passed |
| CRAP | `crap.py .migration/runs/lizard.csv --lcov .migration/runs/crap.lcov --max 30` | 0 | Maximum 7.0; threshold 30 |
| Full mutation | `python .migration/harness/tools/afs-mutation --all` | 0 | Score 0.976; threshold 0.8; 244 killed, 6 survived, base `all` |

The target graph has no data path from either `GET /about` or `GET /ui/about/`; both are static information routes, not missing data flows. The six full-run mutation survivors affect loan catalog templates/context, loan URL routing, fee dataclass mutability, and loan form metadata; none touches library-info.

## Characterization and verification

The only capability in `.migration/slices/library-info.yaml` is `about.page`. Its ledger entry `.migration/ledger/about.page.yaml` is `migrated` with `differential` verification and tier A characterization.

- **LL-04 implementation:** The Tier-A golden and target HTTP test show `GET /about` returns HTTP 200, `text/html`, and the same static HTML body. The separate target addition at `/ui/about/` renders the library description, opening hours, 14-day lending period, contact link, and Loans navigation in the approved reading-room layout. The HTTP and browser tests cover these routes and reject non-GET requests.
- **Verification history:** The first verifier run (#104, PR #105) was blocked by unrelated loan-browser and mutation-collector failures. Those were addressed before the re-verification (#113, PR #115), whose verifier return is `pass`; the acceptance run's full suite and full mutation gate also passed.
- **Audit:** LI-AUDIT (#122, PR #125) independently checked the capability, graph paths, plan and quirk decisions, test-first evidence, and mutation survivors. It returned `complete` with no capability gaps or graph inconsistencies.
- **Quirks:** The cited decisions #39–#43 are approved fixes for other loan capabilities; none changes the About page boundary. No new quirk ticket was found during acceptance.

| Capability | Ledger status | Verification | Evidence / result |
|---|---|---|---|
| `about.page` | `migrated` | `differential` | Tier-A `/about` golden comparison; executable HTTP/browser tests; LL-04 verifier `pass`; LI-AUDIT `complete`; no coverage gaps |

## Ticket reconciliation

Epic #64 has five descendants. The reconciliation records the completed implementation and audit tickets, both verification tickets (with #104 attributed through its parent-ticket return continuation in PRs #105 and #115), and this acceptance ticket completed by PR #128.

## Human check

**Requested; not signed off.** Have the operator compare the legacy `GET /about` page with target `GET /about` and `GET /ui/about/`, checking the library text and details: name/description, opening hours, 14-day lending policy, and contact information/link. Then compare the target `/ui/about/` layout with the approved `reading-room` decisions in the library-information plan. The modernized `/ui/about/` route is a target addition with no legacy route, so assess its layout against the plan, while checking that it retains the legacy page's library information.
