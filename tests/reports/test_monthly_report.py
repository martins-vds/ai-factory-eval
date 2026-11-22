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
    due_on: date
    returned_on: date | None = None


@dataclass
class Fee:
    amount_cents: int


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def started_between(self, start, end):
        return [loan for loan in self.loans if start <= loan.lent_on < end]


class FeeCalculator:
    def __init__(self, fees):
        self.fees = fees

    def fee_for(self, loan_id):
        return self.fees[loan_id]


class Clock:
    def __init__(self, today=date(2026, 3, 1)):
        self.value = today

    def today(self):
        return self.value


def test_monthly_report_aggregates_previous_calendar_month_loans():
    application = MonthlyReportApplication(
        LoanRepository(
            [
                Loan('L0', 'member-1', date(2026, 1, 31), date(2026, 2, 14)),
                Loan('L1', 'member-1', date(2026, 2, 1), date(2026, 2, 10), date(2026, 2, 13)),
                Loan('L2', 'member-1', date(2026, 2, 28), date(2026, 3, 14)),
                Loan('L3', 'member-2', date(2026, 3, 1), date(2026, 3, 15)),
            ]
        ),
        FeeCalculator({'L1': Fee(75), 'L2': Fee(0)}),
        Clock(),
    )

    rows = application.generate()

    assert [
        (row.member_id, row.loans_started, row.late_returns, row.late_fees_cents)
        for row in rows
    ] == [('member-1', 2, 1, 75)]


def test_monthly_report_orders_members_by_fees_then_member_id():
    application = MonthlyReportApplication(
        LoanRepository(
            [
                Loan('L1', 'member-z', date(2026, 2, 1), date(2026, 2, 15)),
                Loan('L2', 'member-b', date(2026, 2, 2), date(2026, 2, 16)),
                Loan('L3', 'member-a', date(2026, 2, 3), date(2026, 2, 17)),
                Loan('L4', 'member-c', date(2026, 2, 4), date(2026, 2, 18)),
            ]
        ),
        FeeCalculator(
            {'L1': Fee(75), 'L2': Fee(75), 'L3': Fee(100), 'L4': Fee(0)}
        ),
        Clock(),
    )

    rows = application.generate()

    assert [
        (row.member_id, row.late_fees_cents) for row in rows
    ] == [
        ('member-a', 100),
        ('member-b', 75),
        ('member-z', 75),
        ('member-c', 0),
    ]


def test_monthly_report_handles_previous_month_across_calendar_years():
    application = MonthlyReportApplication(
        LoanRepository(
            [
                Loan('L0', 'member-1', date(2025, 11, 30), date(2025, 12, 14)),
                Loan('L1', 'member-1', date(2025, 12, 1), date(2025, 12, 15)),
                Loan('L2', 'member-1', date(2025, 12, 31), date(2026, 1, 14)),
                Loan('L3', 'member-2', date(2026, 1, 1), date(2026, 1, 15)),
            ]
        ),
        FeeCalculator({'L1': Fee(0), 'L2': Fee(0)}),
        Clock(date(2026, 1, 1)),
    )

    rows = application.generate()

    assert [
        (row.member_id, row.loans_started, row.late_returns, row.late_fees_cents)
        for row in rows
    ] == [('member-1', 2, 0, 0)]


@pytest.mark.django_db
def test_monthly_report_command_prints_previous_month_totals_in_specified_order():
    current_month_start = timezone.localdate().replace(day=1)
    last_month_day = current_month_start - timedelta(days=1)
    month_start = last_month_day.replace(day=1)
    DjangoLoan.objects.all().delete()
    DjangoLoan.objects.bulk_create(
        [
            DjangoLoan(
                id='R1',
                member='member-a',
                isbn='1',
                lent_on=month_start,
                returned_on=month_start + timedelta(days=17),
            ),
            DjangoLoan(
                id='R2',
                member='member-a',
                isbn='2',
                lent_on=month_start + timedelta(days=1),
                returned_on=month_start + timedelta(days=15),
            ),
            DjangoLoan(
                id='R3',
                member='member-b',
                isbn='3',
                lent_on=month_start + timedelta(days=2),
                returned_on=month_start + timedelta(days=19),
            ),
            DjangoLoan(
                id='R4',
                member='member-c',
                isbn='4',
                lent_on=month_start + timedelta(days=3),
                returned_on=month_start + timedelta(days=17),
            ),
            DjangoLoan(
                id='R5',
                member='outside-month',
                isbn='5',
                lent_on=current_month_start,
            ),
        ]
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'member-a,2,1,75\n'
        'member-b,1,1,75\n'
        'member-c,1,0,0\n'
    )
