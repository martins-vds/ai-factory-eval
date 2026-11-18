from dataclasses import dataclass
from datetime import date

from src.reports.services import MonthlyReportApplication, MonthlyReportRow


@dataclass
class Loan:
    id: str
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans
        self.period = None

    def started_in_period(self, start, end):
        self.period = start, end
        return [
            loan
            for loan in self.loans
            if start <= loan.lent_on < end
        ]


class FeeCalculator:
    def __init__(self, fees):
        self.fees = fees

    def fee_for(self, loan_id):
        return self.fees[loan_id]


@dataclass
class Fee:
    amount_cents: int


def test_monthly_report_aggregates_prior_month_and_orders_members_by_fees_then_id():
    repository = LoanRepository(
        [
            Loan('L1', 'zara', date(2026, 2, 1), date(2026, 2, 15), date(2026, 2, 18)),
            Loan('L2', 'amy', date(2026, 2, 2), date(2026, 2, 16), date(2026, 2, 19)),
            Loan('L3', 'dee', date(2026, 2, 3), date(2026, 2, 17), date(2026, 2, 20)),
            Loan('L4', 'outside', date(2026, 1, 31), date(2026, 2, 14), None),
            Loan('L5', 'outside', date(2026, 3, 1), date(2026, 3, 15), None),
        ]
    )
    application = MonthlyReportApplication(
        repository,
        FeeCalculator({'L1': Fee(1000), 'L2': Fee(75), 'L3': Fee(75)}),
    )

    report = application.monthly_report_for(date(2026, 3, 1))

    assert repository.period == (date(2026, 2, 1), date(2026, 3, 1))
    assert report == [
        MonthlyReportRow('zara', 1, 1, 1000),
        MonthlyReportRow('amy', 1, 1, 75),
        MonthlyReportRow('dee', 1, 1, 75),
    ]
