# Slice library-info — acceptance evidence

- Tickets: LL-04 (#65), verifier checks (#104, #113), LI-AUDIT (#122), LI-ACCEPT (#127) · Commit: `7d4b249e342a94e7176ebf3e1d370f81d7156b16` · Acceptance run date: 2026-11-11
- Acceptance run: [42938753426, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42938753426); artifact `afs-acceptance-7d4b249e342a94e7176ebf3e1d370f81d7156b16-42938753426-1`
- Verified archive: `.migration/evidence/acceptance-runs/42938753426-1.json`
- Independent slice audit: `.migration/evidence/library-info/report.md`; LI-AUDIT returned `complete` in PR #125.

## Acceptance run

The archive records `status: passed`, exit 0, repository `martins-vds/ai-factory-synthetic-target`, run attempt 1, and commit `7d4b249e342a94e7176ebf3e1d370f81d7156b16`. GitHub Actions confirms the `graph / understand`, `acceptance`, and `publish` jobs all succeeded for that exact commit. The run's target graph was built for the same commit.

The archived run's source and target graph gates passed; its target graph reports 27 entry points and 18 reaching data. Both About routes are deliberately non-data routes. Build, idiom, tests, CRAP, and full mutation all passed. The full mutation result is 0.976 (244 killed, 6 survived), above the 0.8 threshold; CRAP maximum is 7.0 against a threshold of 30. The acceptance gates were not rerun for this acceptance session; see the archived result and the unchanged run rows in `.migration/evidence/runs/LI-ACCEPT.md`.

The artifact's stated retention is 30 days from the run, through 2026-12-11.

## Characterization and capability coverage

The only capability in the library-info slice is `about.page`. Its ledger entry remains `migrated` with tier-A `differential` verification; no status change is needed.

| Capability | Target components | Evidence and result |
|---|---|---|
| `about.page` | `config.urls.urlpatterns`; `src.library_info.urls`; `src.library_info.views.about` and `about_page`; `templates/library_info/legacy_about.html`; `templates/library_info/about.html` | The tier-A HTTP golden and `tests/library_info/test_about_page.py::test_about_endpoint_matches_characterized_response` establish that target `GET /about` matches the characterized status, content type, and body. `tests/library_info/test_about_page.py::test_modern_about_page_shows_library_information_in_browser` exercises the separate target `GET /ui/about/` page and its library details. Both routes reject non-GET requests in executable tests. |

The LL-04 journal records failing-first runs for both pages followed by passing focused checks. Its first verification was blocked by full-suite isolation and mutation collection failures (PR #105); the re-verification returned `pass` after fixes (PR #115). The independent audit checked the code, plan, golden, ledger, quirk rulings, and test evidence and returned `complete` with no gaps or graph inconsistencies. The target UI page is an approved addition under the `reading-room` decision; the source has no equivalent modern UI route.

## Mutation survivors

The six full-run survivors concern loan catalog templates/context, loan URL routing, fee dataclass mutability, and loan form metadata. The independent audit found none in the library-info capability. LL-04's final changed-code mutation record is 1.000 (8 killed, 0 survived).

## Human side-by-side check — requested

No human sign-off is recorded or implied here. Please compare:

1. The legacy `GET /about` response against target `GET /about`: exact text and library details, including opening hours, lending policy/14-day period, and contact information.
2. The details in legacy `GET /about` against those rendered by target `GET /ui/about/`: library name and description, opening hours, 14-day lending period, and contact link. The modern UI route is a target addition and has no legacy route counterpart.
3. Target `/ui/about/` layout and asset delivery against the approved `reading-room` layout and the library-information plan, including the Tailwind/daisyUI and pinned htmx pattern.

The result remains `requested` until the operator performs and reports this comparison.
