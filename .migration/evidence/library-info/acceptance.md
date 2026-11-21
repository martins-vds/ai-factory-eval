# Slice library-info — acceptance evidence

- Slice epic: `martins-vds/ai-factory-synthetic-target#64`
- Tickets: LL-04 (#65), verification (#104), re-verification (#113), LI-AUDIT (#122), LI-ACCEPT (#127)
- Acceptance run: [42938753426, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42938753426)
- Executed commit: `7d4b249e342a94e7176ebf3e1d370f81d7156b16`
- Archived result: `.migration/evidence/acceptance-runs/42938753426-1.json`
- Report date: 2026-11-21

The archived acceptance run reports success for all planned gates. This session did not rerun gates or mutation. The result archive and completed audit are the evidence for the recorded results below. The operator's side-by-side check remains requested; this report is not human sign-off or approval.

## Descendant tickets

The four work and audit descendants are closed as completed: LL-04 (#65) landed in PR #103; its initial verifier ticket #104 landed in PR #105, followed by passing re-verification #113 in PR #115; LI-AUDIT (#122) returned `complete` in PR #125. This acceptance ticket (#127) is still open pending its PR.

## Acceptance run

| Gate | Command | Exit | Notes |
|---|---|---:|---|
| Runtime, harness integrity, services, graph freshness | Profile preflight commands recorded in the archive | 0 | All preflights passed. |
| Source graph | `graph_gate.py --side source --require-graph` | 0 | 8 entry points; 6 reaching data. |
| Target graph | `graph_gate.py --side target --require-graph --enforce-ownership` | 0 | 27 entry points; 18 reaching data. `/about` and `/ui/about/` have no data path, as expected for static information pages. |
| Build | `python -m compileall -q src`; `python manage.py check` | 0 | Both passed. |
| Idiom | `ruff check src config manage.py tests`; `ruff format --check src config manage.py tests` | 0 | Both passed. |
| Tests | `pytest -q` | 0 | Full suite passed. |
| CRAP | `crap.py ... --max 30` | 0 | Maximum 7.0; threshold 30. |
| Full mutation | `afs-mutation --all` | 0 | Score 0.976; threshold 0.8; 244 killed, 6 survived, `base=all`. |

The six full-run survivors concern loan catalog templates/context, loan URL routing, fee dataclass mutability, and loan form metadata; none touches library information. The detailed acceptance run record is in the archive above. Its gate journal rows have been copied unchanged from `.migration/evidence/runs/LI-AUDIT.md` into `.migration/evidence/runs/LI-ACCEPT.md`; this session's setup-probe is also recorded there.

## Characterization and capability coverage

Characterization is tier A. The legacy `GET /about` golden specifies HTTP 200, `text/html`, and exact static HTML. LL-04's differential check reports a byte-for-byte match at the target `/about` route.

The target's `/ui/about/` is a separate, approved browser page (not a legacy route). It presents the library description, opening hours, 14-day lending period, and mailto contact in the approved reading-room layout. The HTTP and browser behavior tests cover the characterized route and the modern page, including rejection of non-GET requests.

| Capability | Ledger status / verification | Target components and evidence |
|---|---|---|
| `about.page` | `migrated` / `differential`, tier A | `config.urls.urlpatterns`, `src.library_info.urls`, `src.library_info.views.about`, `src.library_info.views.about_page`, `templates/library_info/legacy_about.html`, and `templates/library_info/about.html`; HTTP golden and browser tests listed in `.migration/ledger/about.page.yaml`. |

The ledger entry remains unchanged: the auditor verified its components and executable evidence and found no coverage gap.

## Verification and audit

LL-04 landed in PR #103. Its initial verification (#104, PR #105) was blocked by test-isolation and mutation-collection failures. The fixes were re-verified in #113 / PR #115, whose return is `pass`. LI-AUDIT #122 landed in PR #125 with `verdict: complete`, one capability checked, no gaps, and no graph inconsistencies. Its report is `.migration/evidence/library-info/report.md`.

The approved quirk rulings #39–#43 concern other capabilities (loan-field validation, payment interruption, repeated returns, persistence, and export); none changes the About page boundary.

## Human side-by-side check — requested

Compare the legacy application against the target, side by side:

1. Compare legacy `GET /about` with target `GET /about`: verify the About text and library details, especially opening hours, lending policy, and contact information, are unchanged.
2. Compare those same library details from legacy `GET /about` with target `GET /ui/about/`: verify the modern page retains the description, hours, 14-day lending term, and contact address.
3. Compare the target `/ui/about/` layout with the approved `reading-room` variant and modernization decisions in the plan/map; do not treat the modernized visual layout as a legacy behavior requirement.

Record the human review and any mismatches on LI-ACCEPT (#127). No outcome or approval is recorded here.
