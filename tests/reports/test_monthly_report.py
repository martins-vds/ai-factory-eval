from dataclasses import dataclass
from datetime import date, timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan
from src.reports.services import MonthlyReportApplication


@dataclass
class ReportLoan:
    id: str
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None = None


@dataclass
class Fee:
    days_late: int
    amount_cents: int


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans
        self.period = None

    def started_between(self, start, end):
        self.period = (start, end)
        return [loan for loan in self.loans if start <= loan.lent_on < end]


class FeeCalculator:
    def __init__(self, fees):
        self.fees = fees

    def fee_for(self, loan_id):
        return self.fees.get(loan_id)


class Clock:
    def today(self):
        return date(2026, 1, 1)


def test_monthly_report_groups_prior_month_and_orders_by_fees_then_member():
    repository = LoanRepository(
        [
            ReportLoan('Z1', 'zoe', date(2025, 12, 3), date(2025, 12, 17), date(2025, 12, 20)),
            ReportLoan('Z2', 'zoe', date(2025, 12, 4), date(2025, 12, 18)),
            ReportLoan('A1', 'amy', date(2025, 12, 5), date(2025, 12, 19), date(2025, 12, 22)),
            ReportLoan('Y1', 'yara', date(2025, 12, 6), date(2025, 12, 20), date(2025, 12, 24)),
            ReportLoan('N1', 'nina', date(2025, 12, 6), date(2025, 12, 20)),
            ReportLoan('OUT', 'outside', date(2026, 1, 1), date(2026, 1, 15)),
        ]
    )
    fees = FeeCalculator(
        {
            'Z1': Fee(days_late=3, amount_cents=75),
            'Z2': Fee(days_late=4, amount_cents=100),
            'A1': Fee(days_late=7, amount_cents=175),
            'Y1': Fee(days_late=4, amount_cents=100),
            'N1': Fee(days_late=0, amount_cents=0),
        }
    )
    report = MonthlyReportApplication(repository, fees, Clock())

    rows = report.generate()

    assert repository.period == (date(2025, 12, 1), date(2026, 1, 1))
    assert [
        (row.member_id, row.loans_started, row.late_returns, row.late_fees_cents)
        for row in rows
    ] == [
        ('amy', 1, 1, 175),
        ('zoe', 2, 1, 175),
        ('yara', 1, 1, 100),
        ('nina', 1, 0, 0),
    ]


@pytest.mark.django_db
def test_monthly_report_command_prints_the_prior_month_report_from_postgres():
    today = timezone.localdate()
    month_end = today.replace(day=1)
    previous_month_start = (month_end - timedelta(days=1)).replace(day=1)
    lent_on = previous_month_start
    due_on = lent_on + timedelta(days=14)
    returned_on = due_on + timedelta(days=3)
    Loan.objects.create(
        id='REPORT-1',
        member='report-reader',
        isbn='report-isbn',
        lent_on=lent_on,
        returned_on=returned_on,
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id;loans_started;late_returns;late_fees_cents\n'
        'report-reader;1;1;75\n'
    )
