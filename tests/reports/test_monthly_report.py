from dataclasses import dataclass
from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan as DjangoLoan
from src.reports.services import MemberMonthlyReport, MonthlyReportApplication


@dataclass(frozen=True)
class Loan:
    id: str
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans
        self.requested_period = None

    def for_period(self, start_on, end_before):
        self.requested_period = (start_on, end_before)
        return self.loans


def test_monthly_report_aggregates_previous_month_and_sorts_by_fees_then_member():
    repository = LoanRepository(
        [
            Loan('L1', 'amy', date(2026, 2, 3), date(2026, 2, 10), date(2026, 2, 16)),
            Loan('L2', 'amy', date(2026, 2, 4), date(2026, 2, 10), date(2026, 2, 11)),
            Loan('L8', 'amy', date(2026, 2, 1), date(2026, 1, 29), date(2026, 2, 1)),
            Loan('L3', 'ben', date(2026, 2, 1), date(2026, 2, 2), date(2026, 2, 4)),
            Loan('L4', 'zoe', date(2026, 2, 2), date(2026, 2, 8), date(2026, 2, 8)),
            Loan('L5', 'max', date(2026, 2, 2), date(2025, 11, 7), date(2026, 2, 15)),
            Loan('L6', 'outside', date(2026, 1, 31), date(2026, 2, 2), date(2026, 2, 5)),
            Loan('L7', 'outside', date(2026, 3, 1), date(2026, 3, 15), None),
        ]
    )
    application = MonthlyReportApplication(repository)

    report = application.generate(date(2026, 3, 1))

    assert repository.requested_period == (date(2026, 2, 1), date(2026, 3, 1))
    assert report == [
        MemberMonthlyReport('max', 1, 1, 1000),
        MemberMonthlyReport('amy', 3, 3, 225),
        MemberMonthlyReport('ben', 1, 1, 0),
        MemberMonthlyReport('zoe', 1, 0, 0),
    ]


@pytest.mark.django_db
def test_monthly_report_command_reads_persisted_loans(monkeypatch):
    as_of = date(2099, 3, 1)
    monkeypatch.setattr(timezone, 'localdate', lambda: as_of)
    DjangoLoan.objects.create(
        id='LL05-report-1',
        member='reader',
        isbn='report-1',
        lent_on=date(2099, 2, 2),
        returned_on=date(2099, 2, 19),
    )
    DjangoLoan.objects.create(
        id='LL05-report-2',
        member='reader',
        isbn='report-2',
        lent_on=date(2099, 1, 30),
        returned_on=date(2099, 2, 19),
    )
    DjangoLoan.objects.create(
        id='LL05-report-3',
        member='reader',
        isbn='report-3',
        lent_on=date(2099, 2, 4),
        returned_on=date(2099, 3, 1),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue().splitlines() == [
        'member_id,loans_started,late_returns,late_fees_cents',
        'reader,2,2,225',
    ]
