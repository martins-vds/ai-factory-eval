from dataclasses import dataclass
from datetime import date, timedelta

from src.fees.services import FeeApplication
from src.reports.services import MonthlyReportApplication, MonthlyReportRow


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
        return date(2026, 11, 1)


class PaymentGateway:
    def charge(self, loan_id):
        raise AssertionError('monthly report must not charge the payment gateway')


def test_monthly_report_aggregates_the_previous_calendar_month():
    repository = LoanRepository(
        [
            Loan('L1', 'ada', date(2026, 10, 1), date(2026, 10, 18)),
            Loan('L2', 'ada', date(2026, 10, 31)),
            Loan('L3', 'bea', date(2026, 10, 2), date(2026, 10, 20)),
            Loan('L4', 'zoe', date(2026, 10, 3), date(2026, 10, 20)),
            Loan('L5', 'old-member', date(2026, 9, 30), date(2026, 10, 20)),
            Loan('L6', 'new-member', date(2026, 11, 1)),
        ]
    )
    clock = FixedClock()
    application = MonthlyReportApplication(
        repository,
        FeeApplication(repository, clock, PaymentGateway()),
        clock,
    )

    rows = application.generate()

    assert rows == [
        MonthlyReportRow('bea', loans_started=1, late_returns=1, late_fees_cents=100),
        MonthlyReportRow('ada', loans_started=2, late_returns=1, late_fees_cents=75),
        MonthlyReportRow('zoe', loans_started=1, late_returns=1, late_fees_cents=75),
    ]
