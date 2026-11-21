from datetime import date, timedelta
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan
from src.reports.services import MonthlyReportApplication


class InMemoryLoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def all(self):
        return list(self.loans)


class ReportLoan:
    def __init__(self, member, lent_on, returned_on=None, due_on=None):
        self.member = member
        self.lent_on = lent_on
        self.returned_on = returned_on
        self.due_on = due_on or (lent_on + timedelta(days=14))


def test_monthly_report_groups_and_sorts_member_rows():
    loans = [
        ReportLoan('outside', date(2026, 11, 1)),
        ReportLoan('ana', date(2026, 10, 2), date(2026, 10, 20)),
        ReportLoan('ana', date(2026, 10, 15), date(2026, 10, 18)),
        ReportLoan('bo', date(2026, 10, 1)),
        ReportLoan('cy', date(2026, 9, 30)),
    ]
    application = MonthlyReportApplication(InMemoryLoanRepository(loans))

    rows = application.report(date(2026, 10, 1), date(2026, 11, 1))

    assert [
        (row.member, row.loans_started, row.late_returns, row.late_fees_cents) for row in rows
    ] == [
        ('bo', 1, 0, 400),
        ('ana', 2, 1, 100),
    ]


def test_monthly_report_handles_month_end_due_date_and_late_fee_boundaries():
    loans = [
        ReportLoan('edge', date(2026, 10, 1), date(2026, 10, 31), date(2026, 10, 28)),
        ReportLoan('edge', date(2026, 10, 2), date(2026, 10, 16), date(2026, 10, 16)),
        ReportLoan('edge', date(2026, 10, 3), date(2026, 10, 23), date(2026, 10, 20)),
        ReportLoan('due', date(2026, 10, 4), date(2026, 10, 18), date(2026, 10, 18)),
    ]

    rows = MonthlyReportApplication(InMemoryLoanRepository(loans)).report(
        date(2026, 10, 1),
        date(2026, 11, 1),
    )

    assert [
        (row.member, row.loans_started, row.late_returns, row.late_fees_cents) for row in rows
    ] == [
        ('edge', 3, 2, 150),
        ('due', 1, 0, 0),
    ]


@pytest.mark.django_db
def test_monthly_report_command_uses_prior_month_and_does_not_include_other_months():
    timezone.activate(timezone.get_default_timezone())
    Loan.objects.all().delete()
    Loan.objects.bulk_create(
        [
            Loan(
                id='R1',
                member='zoe',
                isbn='1',
                lent_on=date(2026, 10, 3),
                returned_on=date(2026, 10, 20),
            ),
            Loan(
                id='R2',
                member='amy',
                isbn='2',
                lent_on=date(2026, 10, 4),
                returned_on=date(2026, 10, 1),
            ),
            Loan(
                id='R3',
                member='zoe',
                isbn='3',
                lent_on=date(2026, 9, 30),
                returned_on=date(2026, 10, 3),
            ),
        ]
    )

    output = StringIO()
    call_command('monthly_report', '--month=2026-10', stdout=output)

    assert output.getvalue() == 'zoe,1,1,75\namy,1,0,0\n'


@pytest.mark.django_db
def test_monthly_report_command_calculates_january_prior_month():
    Loan.objects.all().delete()
    Loan.objects.create(
        id='DEC1',
        member='december',
        isbn='1',
        lent_on=date(2026, 12, 3),
    )

    output = StringIO()
    with patch(
        'src.reports.management.commands.monthly_report.timezone.localdate',
        return_value=date(2027, 1, 1),
    ):
        call_command('monthly_report', stdout=output)

    assert output.getvalue() == 'december,1,0,350\n'


def test_monthly_report_rejects_invalid_month():
    with pytest.raises(Exception, match='YYYY-MM'):
        call_command('monthly_report', '--month=not-a-month', stdout=StringIO())
