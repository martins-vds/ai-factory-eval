from dataclasses import dataclass
from datetime import date, timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan as DjangoLoan
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
        self.periods = []

    def for_period(self, start, end):
        self.periods.append((start, end))
        return self.loans


def test_monthly_report_aggregates_and_orders_members_with_monthly_loans():
    application = MonthlyReportApplication(
        LoanRepository(
            [
                Loan('L1', 'B', date(2026, 10, 5), date(2026, 10, 22)),
                Loan('L2', 'B', date(2026, 10, 10), date(2026, 10, 30)),
                Loan('L3', 'A', date(2026, 10, 1), date(2026, 10, 18)),
                Loan('L4', 'C', date(2026, 10, 3), date(2026, 10, 25)),
                Loan('L8', 'D', date(2026, 10, 4), date(2026, 10, 22)),
                Loan('L9', 'E', date(2026, 10, 4), date(2026, 10, 22)),
                Loan('L5', 'Z', date(2026, 9, 1), date(2026, 10, 25)),
                Loan('L6', 'BEFORE', date(2026, 9, 30)),
                Loan('L7', 'END', date(2026, 11, 1)),
                Loan('L10', 'A', date(2026, 1, 1), date(2026, 9, 30)),
                Loan('L11', 'A', date(2026, 1, 1), date(2026, 11, 1)),
            ]
        )
    )

    report = application.run(date(2026, 10, 1), date(2026, 11, 1))

    assert [
        (row.member_id, row.loans_started, row.late_returns, row.total_late_fees_cents)
        for row in report
    ] == [
        ('B', 2, 2, 225),
        ('C', 1, 1, 200),
        ('D', 1, 1, 100),
        ('E', 1, 1, 100),
        ('A', 1, 1, 75),
    ]


def test_monthly_report_uses_previous_calendar_month_across_year_boundary():
    repository = LoanRepository([])
    application = MonthlyReportApplication(repository)

    report = application.run_previous_month(date(2027, 1, 1))

    assert report == []
    assert repository.periods == [(date(2026, 12, 1), date(2027, 1, 1))]


@pytest.mark.parametrize(
    ('days_late', 'expected_late_returns', 'expected_fees'),
    [(0, 0, 0), (1, 1, 0), (2, 1, 0), (3, 1, 75), (40, 1, 1000), (100, 1, 1000)],
)
def test_monthly_report_applies_late_return_grace_period_and_fee_cap(
    days_late, expected_late_returns, expected_fees
):
    due_on = date(2026, 10, 14) - timedelta(days=days_late)
    returned_on = due_on + timedelta(days=days_late)
    application = MonthlyReportApplication(
        LoanRepository(
            [
                Loan('L1', 'member', due_on - timedelta(days=14), returned_on),
                Loan('L2', 'member', date(2026, 10, 2)),
            ]
        )
    )

    report = application.run(date(2026, 10, 1), date(2026, 11, 1))

    assert [
        (row.member_id, row.loans_started, row.late_returns, row.total_late_fees_cents)
        for row in report
    ] == [('member', 1, expected_late_returns, expected_fees)]


@pytest.mark.django_db
def test_monthly_report_command_outputs_previous_calendar_month(monkeypatch):
    DjangoLoan.objects.create(
        id='R1',
        member='B',
        isbn='b',
        lent_on=date(2026, 9, 6),
        returned_on=date(2026, 10, 1),
    )
    DjangoLoan.objects.create(
        id='R2',
        member='B',
        isbn='b',
        lent_on=date(2026, 10, 5),
    )
    DjangoLoan.objects.create(
        id='R3',
        member='A',
        isbn='a',
        lent_on=date(2026, 10, 1),
        returned_on=date(2026, 10, 18),
    )
    DjangoLoan.objects.create(
        id='R4',
        member='C',
        isbn='c',
        lent_on=date(2026, 10, 31),
    )
    DjangoLoan.objects.create(
        id='R5',
        member='Z',
        isbn='z',
        lent_on=date(2026, 9, 1),
        returned_on=date(2026, 10, 30),
    )
    DjangoLoan.objects.create(
        id='R6',
        member='END',
        isbn='end',
        lent_on=date(2026, 11, 1),
    )
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 11, 1))
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,total_late_fees_cents\n'
        'B,1,1,275\n'
        'A,1,1,75\n'
        'C,1,0,0\n'
    )
