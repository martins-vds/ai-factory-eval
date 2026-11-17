from dataclasses import dataclass
from datetime import date
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

from src.loans.models import Loan
from src.reports.services import MonthlyReportApplication


@dataclass(frozen=True)
class LoanSnapshot:
    member: str
    lent_on: date
    due_on: date
    returned_on: date


class ReportRepository:
    def __init__(self, loans):
        self.loans = loans

    def loans_with_activity(self, start, end):
        return self.loans


@pytest.mark.django_db
def test_monthly_report_aggregates_previous_month_and_omits_members_without_activity():
    Loan.objects.all().delete()
    Loan.objects.bulk_create(
        [
            Loan(
                id='LL05-A1',
                member='alpha',
                isbn='1',
                lent_on=date(2026, 10, 1),
                returned_on=date(2026, 10, 18),
            ),
            Loan(
                id='LL05-A2',
                member='alpha',
                isbn='2',
                lent_on=date(2026, 9, 26),
                returned_on=date(2026, 10, 12),
            ),
            Loan(
                id='LL05-Z1',
                member='zeta',
                isbn='3',
                lent_on=date(2026, 10, 1),
                returned_on=date(2026, 10, 18),
            ),
            Loan(
                id='LL05-Z2',
                member='zeta',
                isbn='10',
                lent_on=date(2026, 10, 31),
            ),
            Loan(
                id='LL05-B1',
                member='beta',
                isbn='4',
                lent_on=date(2026, 10, 1),
                returned_on=date(2026, 10, 16),
            ),
            Loan(
                id='LL05-C1',
                member='cap',
                isbn='11',
                lent_on=date(2026, 7, 1),
                returned_on=date(2026, 10, 1),
            ),
            Loan(
                id='LL05-G1',
                member='gamma',
                isbn='5',
                lent_on=date(2026, 9, 26),
                returned_on=date(2026, 10, 10),
            ),
            Loan(
                id='LL05-D1',
                member='delta',
                isbn='6',
                lent_on=date(2026, 9, 1),
                returned_on=date(2026, 9, 30),
            ),
            Loan(
                id='LL05-N1',
                member='november',
                isbn='7',
                lent_on=date(2026, 11, 1),
            ),
            Loan(
                id='LL05-N2',
                member='november-return',
                isbn='8',
                lent_on=date(2026, 9, 26),
                returned_on=date(2026, 11, 1),
            ),
        ]
    )
    output = StringIO()

    with patch('django.utils.timezone.localdate', return_value=date(2026, 11, 1)):
        call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,total_late_fees_cents\n'
        'cap,0,1,1000\n'
        'alpha,1,2,75\n'
        'zeta,2,1,75\n'
        'beta,1,1,0\n'
        'gamma,0,0,0\n'
    )


@pytest.mark.django_db
def test_monthly_report_uses_december_when_run_on_first_day_of_january():
    Loan.objects.all().delete()
    Loan.objects.create(
        id='LL05-DEC',
        member='december',
        isbn='9',
        lent_on=date(2025, 12, 31),
    )
    output = StringIO()

    with patch('django.utils.timezone.localdate', return_value=date(2026, 1, 1)):
        call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,total_late_fees_cents\ndecember,1,0,0\n'
    )


def test_monthly_report_continues_after_on_time_return_and_sums_late_fees():
    application = MonthlyReportApplication(
        ReportRepository(
            [
                LoanSnapshot(
                    member='alpha',
                    lent_on=date(2026, 10, 1),
                    due_on=date(2026, 10, 15),
                    returned_on=date(2026, 10, 15),
                ),
                LoanSnapshot(
                    member='alpha',
                    lent_on=date(2026, 9, 10),
                    due_on=date(2026, 9, 24),
                    returned_on=date(2026, 10, 1),
                ),
                LoanSnapshot(
                    member='alpha',
                    lent_on=date(2026, 9, 11),
                    due_on=date(2026, 9, 25),
                    returned_on=date(2026, 10, 2),
                ),
            ]
        )
    )

    rows = application.for_previous_month(date(2026, 11, 1))

    assert [
        (row.member_id, row.loans_started, row.late_returns, row.total_late_fees_cents)
        for row in rows
    ] == [('alpha', 1, 2, 350)]
