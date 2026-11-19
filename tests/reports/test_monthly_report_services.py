from dataclasses import dataclass
from datetime import date, timedelta

from src.fees.services import FeeApplication
from src.reports.services import MonthlyReportApplication


@dataclass
class Loan:
    id: str
    member: str
    lent_on: date
    returned_on: date | None = None

    @property
    def due_on(self):
        return self.lent_on + timedelta(days=14)


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def all(self):
        return self.loans

    def find(self, loan_id):
        return next((loan for loan in self.loans if loan.id == loan_id), None)


class FixedClock:
    def today(self):
        return date(2026, 3, 1)


class PaymentGateway:
    def charge(self, loan_id):
        raise AssertionError('monthly reports must not charge payments')


def test_monthly_report_groups_prior_month_loans_and_orders_by_fees_then_member():
    repository = LoanRepository(
        [
            Loan('L1', 'Alice', date(2026, 2, 1), date(2026, 2, 18)),
            Loan('L2', 'Alice', date(2026, 2, 1)),
            Loan('L7', 'Alice', date(2026, 2, 1), date(2026, 2, 15)),
            Loan('L3', 'Charlie', date(2026, 2, 1), date(2026, 3, 4)),
            Loan('L4', 'Bob', date(2026, 2, 1), date(2026, 2, 10)),
            Loan('L5', 'Excluded', date(2026, 1, 31), date(2026, 2, 20)),
            Loan('L6', 'Excluded', date(2026, 3, 1)),
        ]
    )
    clock = FixedClock()
    fees = FeeApplication(repository, clock, PaymentGateway())
    application = MonthlyReportApplication(repository, fees, clock)

    rows = application.generate()

    assert [
        (row.member_id, row.loans_started, row.late_returns, row.late_fees_cents) for row in rows
    ] == [
        ('Alice', 3, 1, 425),
        ('Charlie', 1, 1, 425),
        ('Bob', 1, 0, 0),
    ]
