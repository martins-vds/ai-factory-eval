from dataclasses import dataclass
from datetime import date

from src.reports.services import MonthlyReportApplication


@dataclass(frozen=True)
class Loan:
    id: str
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans
        self.started_window = None
        self.returned_window = None

    def started_between(self, start, end):
        self.started_window = (start, end)
        return [loan for loan in self.loans if start <= loan.lent_on < end]

    def returned_between(self, start, end):
        self.returned_window = (start, end)
        return [
            loan
            for loan in self.loans
            if loan.returned_on is not None and start <= loan.returned_on < end
        ]


class Clock:
    def __init__(self, today):
        self.value = today

    def today(self):
        return self.value


@dataclass(frozen=True)
class Fee:
    amount_cents: int


class FeeCalculator:
    def __init__(self, fees):
        self.fees = fees
        self.requested_loan_ids = []

    def fee_for(self, loan_id):
        self.requested_loan_ids.append(loan_id)
        return self.fees.get(loan_id)


def test_generate_uses_half_open_previous_calendar_month():
    repository = LoanRepository(
        [
            Loan('start-boundary', 'december', date(2025, 12, 1), date(2025, 12, 10)),
            Loan('end-boundary', 'january', date(2026, 1, 1), date(2026, 1, 10)),
            Loan(
                'return-end-boundary',
                'december',
                date(2025, 12, 30),
                date(2025, 12, 30),
                date(2026, 1, 1),
            ),
        ]
    )
    application = MonthlyReportApplication(
        repository,
        Clock(date(2026, 1, 1)),
        FeeCalculator({}),
    )

    reports = application.generate()

    assert repository.started_window == (date(2025, 12, 1), date(2026, 1, 1))
    assert repository.returned_window == (date(2025, 12, 1), date(2026, 1, 1))
    assert [(report.member_id, report.loans_started, report.late_returns) for report in reports] == [
        ('december', 2, 0)
    ]


def test_generate_omits_members_without_a_loan_started_in_the_report_month():
    repository = LoanRepository(
        [
            Loan('started', 'alice', date(2025, 12, 5), date(2025, 12, 10)),
            Loan(
                'return-only',
                'bob',
                date(2025, 11, 5),
                date(2025, 12, 1),
                date(2025, 12, 10),
            ),
        ]
    )
    application = MonthlyReportApplication(
        repository,
        Clock(date(2026, 1, 15)),
        FeeCalculator({'return-only': Fee(75)}),
    )

    reports = application.generate()

    assert [(report.member_id, report.loans_started) for report in reports] == [('alice', 1)]


def test_generate_counts_only_late_returns_and_sums_calculated_fees():
    repository = LoanRepository(
        [
            Loan('early', 'alice', date(2025, 12, 1), date(2025, 12, 20), date(2025, 12, 19)),
            Loan('on-time', 'alice', date(2025, 12, 2), date(2025, 12, 20), date(2025, 12, 20)),
            Loan('late', 'alice', date(2025, 12, 3), date(2025, 12, 20), date(2025, 12, 21)),
            Loan(
                'late-without-fee',
                'alice',
                date(2025, 12, 4),
                date(2025, 12, 20),
                date(2025, 12, 22),
            ),
        ]
    )
    fees = FeeCalculator({'late': Fee(75)})
    application = MonthlyReportApplication(repository, Clock(date(2026, 1, 15)), fees)

    reports = application.generate()

    assert [(report.late_returns, report.late_fees_cents) for report in reports] == [(2, 75)]
    assert fees.requested_loan_ids == ['late', 'late-without-fee']


def test_generate_orders_by_fees_descending_then_member_id():
    repository = LoanRepository(
        [
            Loan('zeta-loan', 'zeta', date(2025, 12, 1), date(2025, 12, 10), date(2025, 12, 11)),
            Loan(
                'alpha-loan',
                'alpha',
                date(2025, 12, 2),
                date(2025, 12, 10),
                date(2025, 12, 11),
            ),
            Loan(
                'beta-loan',
                'beta',
                date(2025, 12, 3),
                date(2025, 12, 10),
                date(2025, 12, 11),
            ),
        ]
    )
    fees = FeeCalculator(
        {'zeta-loan': Fee(100), 'alpha-loan': Fee(100), 'beta-loan': Fee(200)}
    )
    application = MonthlyReportApplication(repository, Clock(date(2026, 1, 15)), fees)

    reports = application.generate()

    assert [(report.member_id, report.late_fees_cents) for report in reports] == [
        ('beta', 200),
        ('alpha', 100),
        ('zeta', 100),
    ]
