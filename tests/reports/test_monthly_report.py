import csv
from datetime import date
from io import StringIO
from types import SimpleNamespace

import pytest
from django.core.management import call_command
from django.db.models import Model

from src.loans.models import Loan
from src.reports.repository import DjangoMonthlyReportRepository
from src.reports.services import MemberMonthlyReport, MonthlyReportApplication


def test_monthly_report_application_aggregates_previous_month_directly():
    class Loans:
        def __init__(self, records):
            self.records = records
            self.requested_range = None

        def started_between(self, start, end):
            self.requested_range = (start, end)
            return [record for record in self.records if start <= record.lent_on < end]

    class Fees:
        def fee_for(self, loan_id):
            amount = {'L-zeta': 250, 'L-alpha-late': 100, 'L-beta': 100}.get(loan_id)
            return SimpleNamespace(amount_cents=amount) if amount is not None else None

    loans = Loans(
        [
            SimpleNamespace(
                id='L-zeta',
                member='zeta',
                lent_on=date(2025, 12, 1),
                due_on=date(2025, 12, 15),
                returned_on=date(2025, 12, 16),
            ),
            SimpleNamespace(
                id='L-alpha-on-time',
                member='alpha',
                lent_on=date(2025, 12, 2),
                due_on=date(2025, 12, 16),
                returned_on=date(2025, 12, 16),
            ),
            SimpleNamespace(
                id='L-alpha-late',
                member='alpha',
                lent_on=date(2025, 12, 3),
                due_on=date(2025, 12, 17),
                returned_on=date(2025, 12, 18),
            ),
            SimpleNamespace(
                id='L-beta',
                member='beta',
                lent_on=date(2025, 12, 4),
                due_on=date(2025, 12, 18),
                returned_on=None,
            ),
            SimpleNamespace(
                id='L-zero',
                member='zero',
                lent_on=date(2025, 12, 5),
                due_on=date(2025, 12, 19),
                returned_on=date(2025, 12, 19),
            ),
            SimpleNamespace(
                id='L-before',
                member='before',
                lent_on=date(2025, 11, 30),
                due_on=date(2025, 12, 14),
                returned_on=None,
            ),
            SimpleNamespace(
                id='L-after',
                member='after',
                lent_on=date(2026, 1, 1),
                due_on=date(2026, 1, 15),
                returned_on=None,
            ),
        ]
    )
    application = MonthlyReportApplication(loans, Fees())

    reports = application.for_previous_month(date(2026, 1, 1))

    assert loans.requested_range == (date(2025, 12, 1), date(2026, 1, 1))
    assert reports == [
        MemberMonthlyReport('zeta', 1, 1, 250),
        MemberMonthlyReport('alpha', 2, 1, 100),
        MemberMonthlyReport('beta', 1, 0, 100),
        MemberMonthlyReport('zero', 1, 0, 0),
    ]


@pytest.mark.django_db
def test_monthly_report_repository_does_not_pass_orm_rows_to_application():
    Loan.objects.create(
        id='L-report-boundary',
        member='report-boundary',
        isbn='1',
        lent_on=date(2026, 2, 1),
    )

    records = DjangoMonthlyReportRepository().started_between(
        date(2026, 2, 1), date(2026, 3, 1)
    )

    assert all(not isinstance(record, Model) for record in records)


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
