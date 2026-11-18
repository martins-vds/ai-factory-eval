import csv
from datetime import UTC, date, datetime
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from src.loans.models import Loan
from src.reports.services import MonthlyReport


class FixedClock:
    def __init__(self, today):
        self.current_date = today

    def today(self):
        return self.current_date


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans
        self.requested_period = None

    def for_month(self, start, end):
        self.requested_period = (start, end)
        return self.loans


def report_loan(member, lent_on, due_on, returned_on=None):
    return SimpleNamespace(
        member=member,
        lent_on=lent_on,
        due_on=due_on,
        returned_on=returned_on,
    )


def test_monthly_report_uses_prior_month_with_half_open_bounds():
    repository = LoanRepository([])
    report = MonthlyReport(repository, FixedClock(date(2026, 1, 1)))

    report.render()

    assert repository.requested_period == (date(2025, 12, 1), date(2026, 1, 1))


def test_monthly_report_includes_only_members_with_loans_started_in_month():
    repository = LoanRepository(
        [
            report_loan('alpha', date(2025, 12, 1), date(2025, 12, 15)),
            report_loan(
                'alpha',
                date(2025, 11, 1),
                date(2025, 12, 10),
                date(2026, 1, 1),
            ),
            report_loan(
                'return-only',
                date(2025, 11, 1),
                date(2025, 12, 10),
                date(2025, 12, 11),
            ),
            report_loan('next-month', date(2026, 1, 1), date(2026, 1, 15)),
        ]
    )
    report = MonthlyReport(repository, FixedClock(date(2026, 1, 1)))

    rows = list(csv.reader(StringIO(report.render())))

    assert rows == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['alpha', '1', '0', '0'],
    ]


def test_monthly_report_calculates_late_returns_and_fees():
    repository = LoanRepository(
        [
            report_loan('capped', date(2025, 12, 1), date(2025, 12, 15)),
            report_loan(
                'capped',
                date(2025, 11, 1),
                date(2025, 10, 1),
                date(2025, 12, 31),
            ),
            report_loan(
                'charged',
                date(2025, 12, 1),
                date(2025, 12, 10),
                date(2025, 12, 13),
            ),
            report_loan(
                'grace',
                date(2025, 12, 1),
                date(2025, 12, 10),
                date(2025, 12, 12),
            ),
        ]
    )
    report = MonthlyReport(repository, FixedClock(date(2026, 1, 1)))

    rows = list(csv.reader(StringIO(report.render())))

    assert rows == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['capped', '1', '1', '1000'],
        ['charged', '1', '1', '75'],
        ['grace', '1', '1', '0'],
    ]


def test_monthly_report_sorts_fees_descending_then_member_id():
    repository = LoanRepository(
        [
            report_loan(
                'beta',
                date(2025, 12, 1),
                date(2025, 12, 10),
                date(2025, 12, 13),
            ),
            report_loan(
                'alpha',
                date(2025, 12, 1),
                date(2025, 12, 10),
                date(2025, 12, 13),
            ),
            report_loan('zero', date(2025, 12, 1), date(2025, 12, 10)),
        ]
    )
    report = MonthlyReport(repository, FixedClock(date(2026, 1, 1)))

    rows = list(csv.reader(StringIO(report.render())))

    assert [row[0] for row in rows] == ['member_id', 'alpha', 'beta', 'zero']


@pytest.mark.django_db
def test_monthly_report_lists_february_activity_by_fees_then_member_in_local_time():
    Loan.objects.all().delete()
    Loan.objects.create(
        id='L20',
        member='beta',
        isbn='20',
        lent_on=date(2026, 2, 1),
        returned_on=date(2026, 2, 20),
    )
    Loan.objects.create(
        id='L21',
        member='alpha',
        isbn='21',
        lent_on=date(2026, 2, 1),
        returned_on=date(2026, 2, 20),
    )
    Loan.objects.create(
        id='L22',
        member='alpha',
        isbn='22',
        lent_on=date(2026, 2, 2),
    )
    Loan.objects.create(
        id='L25',
        member='alpha',
        isbn='25',
        lent_on=date(2026, 2, 3),
        returned_on=date(2026, 2, 22),
    )
    Loan.objects.create(
        id='L26',
        member='gamma',
        isbn='26',
        lent_on=date(2026, 2, 1),
        returned_on=date(2026, 2, 20),
    )
    Loan.objects.create(
        id='L27',
        member='boundary',
        isbn='27',
        lent_on=date(2026, 2, 1),
        returned_on=date(2026, 2, 18),
    )
    Loan.objects.create(
        id='L28',
        member='start-boundary',
        isbn='28',
        lent_on=date(2026, 1, 17),
        returned_on=date(2026, 2, 1),
    )
    Loan.objects.create(
        id='L29',
        member='start-boundary',
        isbn='29',
        lent_on=date(2026, 2, 2),
    )
    Loan.objects.create(
        id='L23',
        member='not-started-in-month',
        isbn='23',
        lent_on=date(2026, 1, 1),
        returned_on=date(2026, 2, 20),
    )
    Loan.objects.create(
        id='L24',
        member='march',
        isbn='24',
        lent_on=date(2026, 3, 1),
    )

    output = StringIO()
    with (
        override_settings(TIME_ZONE='America/Los_Angeles'),
        patch(
            'django.utils.timezone.now',
            return_value=datetime(2026, 3, 1, 8, 30, tzinfo=UTC),
        ),
    ):
        assert timezone.localdate() == date(2026, 3, 1)
        call_command('monthly_report', stdout=output)

    assert list(csv.reader(StringIO(output.getvalue()))) == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['alpha', '3', '2', '250'],
        ['beta', '1', '1', '125'],
        ['gamma', '1', '1', '125'],
        ['boundary', '1', '1', '75'],
        ['start-boundary', '1', '1', '0'],
    ]


@pytest.mark.django_db
def test_monthly_report_counts_late_returns_and_caps_fees():
    Loan.objects.all().delete()
    Loan.objects.create(
        id='L30',
        member='grace',
        isbn='30',
        lent_on=date(2026, 2, 1),
        returned_on=date(2026, 2, 17),
    )
    Loan.objects.create(
        id='L31',
        member='capped',
        isbn='31',
        lent_on=date(2026, 2, 1),
    )
    Loan.objects.create(
        id='L32',
        member='capped',
        isbn='32',
        lent_on=date(2025, 12, 1),
        returned_on=date(2026, 2, 28),
    )
    Loan.objects.create(
        id='L33',
        member='on-time',
        isbn='33',
        lent_on=date(2026, 2, 1),
        returned_on=date(2026, 2, 15),
    )

    output = StringIO()
    with (
        override_settings(TIME_ZONE='UTC'),
        patch(
            'django.utils.timezone.now',
            return_value=datetime(2026, 3, 1, tzinfo=UTC),
        ),
    ):
        call_command('monthly_report', stdout=output)

    assert list(csv.reader(StringIO(output.getvalue()))) == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['capped', '1', '1', '1000'],
        ['grace', '1', '1', '0'],
        ['on-time', '1', '0', '0'],
    ]
