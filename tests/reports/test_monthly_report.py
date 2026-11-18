from dataclasses import dataclass
from datetime import UTC, date, datetime
import csv
from io import StringIO
from zoneinfo import ZoneInfo

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from src.loans.models import Loan as PersistedLoan
from src.reports.clock import SystemClock
from src.reports.services import MonthlyReportApplication, MonthlyReportRow


@dataclass
class Loan:
    id: str
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


class FixedClock:
    def today(self):
        return date(2026, 3, 1)


def test_monthly_report_aggregates_previous_month_and_orders_fee_ties_by_member():
    repository = LoanRepository(
        [
            Loan('L1', 'ada', date(2026, 2, 1), date(2026, 2, 15), date(2026, 2, 18)),
            Loan('L2', 'ada', date(2026, 2, 27), date(2026, 3, 13)),
            Loan('L3', 'bob', date(2026, 2, 4), date(2026, 2, 18), date(2026, 2, 20)),
            Loan('L4', 'zoe', date(2026, 1, 31), date(2026, 2, 14), date(2026, 2, 20)),
            Loan('L5', 'april', date(2026, 3, 1), date(2026, 3, 15)),
            Loan('L6', 'cara', date(2026, 2, 10), date(2026, 2, 24), date(2026, 2, 24)),
        ]
    )

    rows = MonthlyReportApplication(repository, FixedClock()).run()

    assert repository.period == (date(2026, 2, 1), date(2026, 3, 1))
    assert rows == [
        MonthlyReportRow('ada', loans_started=2, late_returns=1, total_late_fees_cents=75),
        MonthlyReportRow('bob', loans_started=1, late_returns=1, total_late_fees_cents=0),
        MonthlyReportRow('cara', loans_started=1, late_returns=0, total_late_fees_cents=0),
    ]


def test_system_clock_uses_server_default_timezone(monkeypatch):
    instant = datetime(2026, 3, 1, 2, tzinfo=UTC)
    monkeypatch.setattr('src.reports.clock.timezone.now', lambda: instant)

    with override_settings(TIME_ZONE='America/Los_Angeles'):
        timezone.activate(ZoneInfo('Asia/Tokyo'))
        try:
            assert SystemClock().today() == date(2026, 2, 28)
        finally:
            timezone.deactivate()


@pytest.mark.django_db
def test_monthly_report_command_outputs_only_previous_month_loans_as_csv(monkeypatch):
    instant = datetime(2026, 3, 1, tzinfo=UTC)
    monkeypatch.setattr('src.reports.clock.timezone.now', lambda: instant)
    PersistedLoan.objects.create(
        id='LL05-1',
        member='ada, x',
        isbn='1',
        lent_on=date(2026, 2, 1),
        returned_on=date(2026, 2, 18),
    )
    PersistedLoan.objects.create(
        id='LL05-2',
        member='ada, x',
        isbn='2',
        lent_on=date(2026, 2, 27),
    )
    PersistedLoan.objects.create(
        id='LL05-3',
        member='bob',
        isbn='3',
        lent_on=date(2026, 2, 4),
        returned_on=date(2026, 2, 20),
    )
    PersistedLoan.objects.create(
        id='LL05-4',
        member='jan-only',
        isbn='4',
        lent_on=date(2026, 1, 31),
    )
    PersistedLoan.objects.create(
        id='LL05-5',
        member='march-only',
        isbn='5',
        lent_on=date(2026, 3, 1),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert list(csv.reader(StringIO(output.getvalue()))) == [
        ['member_id', 'loans_started', 'late_returns', 'total_late_fees_cents'],
        ['ada, x', '2', '1', '75'],
        ['bob', '1', '1', '0'],
    ]
