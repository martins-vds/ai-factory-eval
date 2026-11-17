import csv
from datetime import date
from io import StringIO
from types import SimpleNamespace

import pytest
from django.core.management import call_command

from src.loans.models import Loan
from src.reports.services import MemberMonthlyReport, MonthlyReportApplication


@pytest.mark.django_db
def test_monthly_report_summarizes_previous_month_loans_in_specified_order(monkeypatch):
    Loan.objects.all().delete()
    Loan.objects.bulk_create(
        [
            Loan(
                id='L-alpha',
                member='alpha',
                isbn='1',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 2, 25),
            ),
            Loan(
                id='L-beta',
                member='beta',
                isbn='2',
                lent_on=date(2026, 2, 2),
                returned_on=date(2026, 2, 26),
            ),
            Loan(
                id='L-zeta-1',
                member='zeta',
                isbn='3',
                lent_on=date(2026, 2, 3),
                returned_on=date(2026, 2, 20),
            ),
            Loan(
                id='L-zeta-2',
                member='zeta',
                isbn='4',
                lent_on=date(2026, 2, 4),
                returned_on=date(2026, 2, 18),
            ),
            Loan(
                id='L-zeta-3',
                member='zeta',
                isbn='7',
                lent_on=date(2026, 2, 5),
                returned_on=date(2026, 2, 20),
            ),
            Loan(
                id='L-zeta-4',
                member='zeta',
                isbn='8',
                lent_on=date(2026, 2, 6),
                returned_on=date(2026, 2, 22),
            ),
            Loan(
                id='L-zeta-5',
                member='zeta',
                isbn='9',
                lent_on=date(2026, 2, 7),
                returned_on=date(2026, 2, 24),
            ),
            Loan(
                id='L-max',
                member='max',
                isbn='10',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 3, 30),
            ),
            Loan(
                id='L-before',
                member='before',
                isbn='5',
                lent_on=date(2026, 1, 31),
            ),
            Loan(
                id='L-after',
                member='after',
                isbn='6',
                lent_on=date(2026, 3, 1),
            ),
            Loan(
                id='L-last-day',
                member='last-day',
                isbn='11',
                lent_on=date(2026, 2, 28),
            ),
        ]
    )
    monkeypatch.setattr(
        'src.reports.management.commands.monthly_report.timezone.localdate',
        lambda: date(2026, 3, 1),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert list(csv.reader(StringIO(output.getvalue()))) == [
        ['member_id', 'loans_started', 'late_returns', 'total_late_fees_cents'],
        ['max', '1', '1', '1000'],
        ['alpha', '1', '1', '250'],
        ['beta', '1', '1', '250'],
        ['zeta', '5', '4', '150'],
        ['last-day', '1', '0', '0'],
    ]


@pytest.mark.django_db
def test_monthly_report_uses_previous_calendar_year_for_january_run(monkeypatch):
    Loan.objects.all().delete()
    Loan.objects.create(
        id='L-december',
        member='dee',
        isbn='1',
        lent_on=date(2025, 12, 1),
    )
    monkeypatch.setattr(
        'src.reports.management.commands.monthly_report.timezone.localdate',
        lambda: date(2026, 1, 1),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert list(csv.reader(StringIO(output.getvalue()))) == [
        ['member_id', 'loans_started', 'late_returns', 'total_late_fees_cents'],
        ['dee', '1', '0', '425'],
    ]


def test_monthly_report_application_aggregates_and_sorts_previous_month():
    class Loans:
        def __init__(self):
            self.requested_range = None

        def started_between(self, start, end):
            self.requested_range = (start, end)
            return [
                SimpleNamespace(
                    id='L-alpha-late',
                    member='alpha',
                    due_on=date(2026, 2, 10),
                    returned_on=date(2026, 2, 13),
                ),
                SimpleNamespace(
                    id='L-alpha-on-time',
                    member='alpha',
                    due_on=date(2026, 2, 12),
                    returned_on=date(2026, 2, 12),
                ),
                SimpleNamespace(
                    id='L-beta-late',
                    member='beta',
                    due_on=date(2026, 2, 10),
                    returned_on=date(2026, 2, 13),
                ),
                SimpleNamespace(
                    id='L-charlie-late',
                    member='charlie',
                    due_on=date(2026, 2, 10),
                    returned_on=date(2026, 2, 14),
                ),
            ]

    class Fees:
        def __init__(self):
            self.amounts = {
                'L-alpha-late': 75,
                'L-alpha-on-time': 0,
                'L-beta-late': 75,
                'L-charlie-late': 100,
            }

        def fee_for(self, loan_id):
            return SimpleNamespace(amount_cents=self.amounts[loan_id])

    loans = Loans()
    reports = MonthlyReportApplication(loans, Fees()).for_previous_month(date(2026, 3, 1))

    assert loans.requested_range == (date(2026, 2, 1), date(2026, 3, 1))
    assert reports == [
        MemberMonthlyReport('charlie', 1, 1, 100),
        MemberMonthlyReport('alpha', 2, 1, 75),
        MemberMonthlyReport('beta', 1, 1, 75),
    ]


def test_monthly_report_application_returns_no_rows_without_loans():
    class Loans:
        def started_between(self, start, end):
            return []

    class Fees:
        def fee_for(self, loan_id):
            raise AssertionError('no fee should be calculated without loans')

    reports = MonthlyReportApplication(Loans(), Fees()).for_previous_month(date(2026, 3, 1))

    assert reports == []
