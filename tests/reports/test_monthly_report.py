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


def test_monthly_report_application_applies_previous_month_rules():
    loans = [
        SimpleNamespace(
            id='L-alpha-on-time',
            member='alpha',
            lent_on=date(2025, 12, 1),
            due_on=date(2025, 12, 10),
            returned_on=date(2025, 12, 10),
        ),
        SimpleNamespace(
            id='L-alpha-late',
            member='alpha',
            lent_on=date(2025, 12, 31),
            due_on=date(2025, 12, 31),
            returned_on=date(2026, 1, 1),
        ),
        SimpleNamespace(
            id='L-bravo-unreturned',
            member='bravo',
            lent_on=date(2025, 12, 30),
            due_on=date(2026, 1, 13),
            returned_on=None,
        ),
        SimpleNamespace(
            id='L-charlie-late',
            member='charlie',
            lent_on=date(2025, 12, 15),
            due_on=date(2025, 12, 22),
            returned_on=date(2026, 1, 2),
        ),
        SimpleNamespace(
            id='L-november',
            member='outside',
            lent_on=date(2025, 11, 30),
            due_on=date(2025, 12, 14),
            returned_on=None,
        ),
        SimpleNamespace(
            id='L-january',
            member='outside',
            lent_on=date(2026, 1, 1),
            due_on=date(2026, 1, 15),
            returned_on=None,
        ),
    ]

    class Loans:
        window = None

        def started_between(self, start, end):
            self.window = (start, end)
            return [loan for loan in loans if start <= loan.lent_on < end]

    class Fees:
        amounts = {
            'L-alpha-on-time': 125,
            'L-alpha-late': 125,
            'L-bravo-unreturned': 250,
            'L-charlie-late': 500,
            'L-november': 900,
            'L-january': 900,
        }

        def fee_for(self, loan_id):
            return SimpleNamespace(amount_cents=self.amounts[loan_id])

    repository = Loans()
    reports = MonthlyReportApplication(repository, Fees()).for_previous_month(
        date(2026, 1, 1)
    )

    assert repository.window == (date(2025, 12, 1), date(2026, 1, 1))
    assert reports == [
        MemberMonthlyReport('charlie', 1, 1, 500),
        MemberMonthlyReport('alpha', 2, 1, 250),
        MemberMonthlyReport('bravo', 1, 0, 250),
    ]
