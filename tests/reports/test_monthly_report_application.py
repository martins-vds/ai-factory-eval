from dataclasses import dataclass
from datetime import date

from src.reports.services import MemberMonthlyReport, MonthlyReportApplication


@dataclass(frozen=True)
class _Loan:
    id: str
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


@dataclass(frozen=True)
class _Fee:
    amount_cents: int


class _Loans:
    def __init__(self, records):
        self.records = records
        self.window = None

    def started_between(self, start, end):
        self.window = (start, end)
        return [loan for loan in self.records if start <= loan.lent_on < end]


class _Fees:
    def __init__(self, amounts):
        self.amounts = amounts

    def fee_for(self, loan_id):
        amount = self.amounts.get(loan_id)
        return None if amount is None else _Fee(amount)


def test_application_aggregates_previous_month_loans_and_excludes_boundary_rows():
    loans = _Loans(
        [
            _Loan('before', 'before', date(2026, 1, 31), date(2026, 2, 14), None),
            _Loan('alpha-late', 'alpha', date(2026, 2, 1), date(2026, 2, 5), date(2026, 2, 6)),
            _Loan('alpha-open', 'alpha', date(2026, 2, 28), date(2026, 3, 14), None),
            _Loan('beta-on-time', 'beta', date(2026, 2, 28), date(2026, 2, 28), date(2026, 2, 28)),
            _Loan('after', 'after', date(2026, 3, 1), date(2026, 3, 15), None),
        ]
    )
    application = MonthlyReportApplication(loans, _Fees({'alpha-late': 125, 'beta-on-time': 125}))

    reports = application.for_previous_month(date(2026, 3, 1))

    assert loans.window == (date(2026, 2, 1), date(2026, 3, 1))
    assert reports == [
        MemberMonthlyReport('alpha', 2, 1, 125),
        MemberMonthlyReport('beta', 1, 0, 125),
    ]
