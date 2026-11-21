# Quirk: Monthly late-fee attribution date is unspecified

## Question
The surviving monthly report specification includes total late fees but does not state whether a fee belongs to the loan's start month, return month, or the month in which it accrues. Which date should attribute a fee to this report?

## Evidence
- Source: `legacy/docs/reports-spec.md:3-6` at the pinned SHA; only the tier-C specification remains.
- Characterization: `.migration/references/characterization-SY-05.md` records that no report runtime or output is available.
- Plan: `.migration/plan/monthly-report.md` specifies a prior-month window but does not settle fee attribution.
- Current WIP behavior: the report sums fees for loans returned during the report month; this is provisional, not an approved ruling.

## Why it looks wrong
Loan-start, return, and accrued-balance attribution can produce different totals for the same month, and the source specification cannot distinguish among them.

## Impact
- Ledger capabilities: `reports.monthly-spec`
- Blocks: `martins-vds/ai-factory-eval#1920`

## Options
1. Attribute each fee to the month the loan is returned.
2. Attribute each fee to the month the loan is started.
3. Include fees accrued during the report month, including for loans not yet returned.
4. Other.
