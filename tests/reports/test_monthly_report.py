from dataclasses import dataclass
from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command

from src.loans.models import Loan as DjangoLoan
from src.reports.services import MonthlyReportApplication, MonthlyReportRow


@dataclass
class Loan:
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans
        self.period = None

    def started_between(self, start, end):
        self.period = (start, end)
        return [loan for loan in self.loans if start <= loan.lent_on < end]


def test_monthly_report_aggregates_prior_month_and_orders_members():
    repository = LoanRepository(
        [
            Loan('member-b', date(2026, 2, 1), date(2026, 2, 15), date(2026, 2, 18)),
            Loan('member-a', date(2026, 2, 2), date(2026, 2, 16), date(2026, 2, 18)),
            Loan('member-c', date(2026, 2, 3), date(2026, 2, 17)),
            Loan('member-a', date(2026, 2, 4), date(2026, 2, 18), date(2026, 2, 20)),
            Loan('member-b', date(2026, 2, 10), date(2026, 2, 24), date(2026, 2, 27)),
            Loan('member-d', date(2026, 2, 5), date(2026, 2, 19), date(2026, 2, 19)),
            Loan('outside-month', date(2026, 1, 31), date(2026, 2, 14), date(2026, 2, 17)),
            Loan('next-month', date(2026, 3, 1), date(2026, 3, 15)),
        ]
    )

    report = MonthlyReportApplication(repository).run(date(2026, 3, 1))

    assert repository.period == (date(2026, 2, 1), date(2026, 3, 1))
    assert report == [
        MonthlyReportRow('member-c', 1, 0, 300),
        MonthlyReportRow('member-b', 2, 2, 150),
        MonthlyReportRow('member-a', 2, 2, 0),
        MonthlyReportRow('member-d', 1, 0, 0),
    ]
    assert report[-2].late_fees_cents == report[-1].late_fees_cents == 0
    assert [row.member_id for row in report[-2:]] == ['member-a', 'member-d']


@pytest.mark.django_db
def test_monthly_report_command_prints_the_prior_month_from_persisted_loans(monkeypatch):
    DjangoLoan.objects.create(
        id='monthly-b',
        member='member-b',
        isbn='isbn-b',
        lent_on=date(2026, 2, 1),
        returned_on=date(2026, 2, 18),
    )
    DjangoLoan.objects.create(
        id='monthly-c',
        member='member-c',
        isbn='isbn-c',
        lent_on=date(2026, 2, 3),
    )
    DjangoLoan.objects.create(
        id='monthly-outside',
        member='outside-month',
        isbn='isbn-outside',
        lent_on=date(2026, 1, 31),
    )
    output = StringIO()
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 3, 1))

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\nmember-c,1,0,300\nmember-b,1,1,75\n'
    )
