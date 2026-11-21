# Fees and payments — slice acceptance

- Slice: `fees-payments`
- Acceptance run: [42912984554, attempt 1](https://github.com/martins-vds/ai-factory-synthetic-target/actions/runs/42912984554)
- Gated commit: `8f9a11640eef9801378f3db53a76903363c5e5b5`
- Report date: 2026-11-21
- Tickets: LL-03 (#63), first verification (#90), re-verification (#96), LF-AUDIT (#114), LF-ACCEPT (#117)

## Acceptance provenance

GitHub reports the `AFS acceptance gates` workflow completed successfully on `main`, at the exact
commit and attempt above. The downloaded artifact ZIP SHA-256 matches GitHub's artifact digest
(`a907578356db5d3f689b4a08a7cb4dd7f7ee3cd5b7e9ad68bc4f859bb39a1af8`); its `result.json` is
byte-identical to `.migration/evidence/acceptance-runs/42912984554-1.json`
(`d819963580a985d4e441f23f599dfc1fc01d786dde2d197d10f71087cbb08364`). The artifact expires
2026-12-10 22:28:25 UTC. The acceptance rows in the committed
`.migration/evidence/runs/LF-ACCEPT.md` are preserved from the artifact's `journals/LF-ACCEPT.md`.

The independent Auditor's report records a successful `afs-acceptance verify` for this run and
commit, an audit verdict of `complete`, and no coverage gaps or graph inconsistencies. In this
evaluation checkout, repeating that verifier returned `artifact execution inputs do not match this
checkout`: the current profile and installed harness differ from the artifact's captured inputs.
No acceptance gate or mutation was rerun or substituted by the coordinator; the accepted result is
the exact archived run audited by LF-AUDIT.

## Gates

All commands below are from the verified acceptance run; each exited 0.

| Gate | Command(s) | Result |
|---|---|---|
| Runtime and harness integrity | `check_runtime.py`; `check_installed.py` | Python 3.13; installed pins valid |
| Services and graph freshness | `afs-services check`; `check_graph_fresh.py --require source,target` | Services healthy; both graphs fresh |
| Source graph | `graph_gate.py --side source --require-graph` | 8 entry points; 6 reach data |
| Target graph | `graph_gate.py --side target --require-graph --enforce-ownership` | 23 entry points; 18 reach data; 13 owned; none unowned |
| Build | `python -m compileall -q src`; `python manage.py check` | Both passed |
| Idiom | `ruff check src config manage.py tests`; `ruff format --check src config manage.py tests` | Both passed |
| Tests | `pytest -q` | Full suite passed |
| CRAP | Coverage pytest, `lizard --csv src`, then `crap.py ... --max 30` | Maximum 7.0; threshold 30 |
| Full mutation | `python .migration/harness/tools/afs-mutation --all` | 0.975; threshold 0.8; 236 killed, 6 survived, 15 files |

## Characterization and ticket outcomes

Tier A characterization and LL-03 evidence cover the two-day late-fee waiver, 25 cents per late day,
the $10 cap, returned-loan date handling, the fee page and unknown-loan response, and the payment
gateway request and failure behavior. PR #88 landed LL-03 with its migrator return. The first
verification (#90, PR #91) returned `blocked`; the fix was independently re-verified as `pass` in
#96 / PR #97. The independent LF-AUDIT (#114, PR #116) reviewed the slice against the accepted run
and returned `complete`.

All three `fees-payments` ledger entries are `migrated`:

| Capability | Target evidence | Acceptance status |
|---|---|---|
| `fees.calculation` | `FeeApplication.fee_for`; `tests/fees/test_fee_calculation.py`; LL-03 differential evidence | Migrated; auditor found no gap |
| `fees.page` | Fee API/UI handlers and templates; `tests/fees/test_endpoints.py`; LL-03 differential evidence | Migrated; auditor found no gap |
| `integration.payment-gateway` | `FeeApplication.pay`, gateway port/adapter and composition; endpoint/gateway tests and characterization golden | Migrated; auditor found no gap |

The Auditor reported six surviving mutants. Four concern loan views/routes/forms outside this slice;
the two fee survivors make internal value objects mutable. The Auditor reviewed them as equivalent
for the observable fee/payment contract and recorded no missing capability. Approved quirk rulings
#40 and #42 were reviewed; the ledger links #40 to the gateway capability.

## Ticket reconciliation

The five in-scope descendants are recorded in
`.migration/evidence/ticket-reconciliation/62.yaml`. The #90 verifier continuation is attributed
through its verifier return's same path, ticket, and role: PR #91 contains the initial return and
PR #97 contains the passing continuation. LF-ACCEPT is recorded against the open PR #118, which
closes #117 when merged; its reconciliation is checked as if that PR were merged. The local
`reconcile_epic.py --dry-run` could not query the issue tree (`gh api` returned HTTP 403), so the
dispositions were assembled from the readable issue and PR records and are subject to the PR's
as-if-merged reconciliation check.

## Human side-by-side check — requested

Compare the legacy application against the target using equivalent loan records, dates, and gateway
responses. Check:

1. For an overdue loan, the fee amount and rounding (including the two-day waiver and $10 cap).
2. For a loan that is not overdue, that no fee is charged or displayed.
3. For an unknown loan, compare the API status/body and the fee page's not-found behavior.
4. Pay through both the API and UI; compare the gateway request and successful status/body or UI
   result.
5. Trigger a non-200 response and an I/O/interruption failure at the gateway; compare the resulting
   API status/body and user-visible UI behavior.

This is a request for human comparison only; no side-by-side sign-off has been recorded.
