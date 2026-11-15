import csv
from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_aggregates_previous_month_loans(monkeypatch):
    Loan.objects.all().delete()
    Loan.objects.bulk_create(
        [
            Loan('zeta-1', 'zeta', '100', date(2026, 1, 2), date(2026, 1, 19)),
            Loan('alpha-1', 'alpha', '101', date(2026, 1, 5), date(2026, 1, 24)),
            Loan('alpha-2', 'alpha', '102', date(2026, 1, 12), date(2026, 1, 28)),
            Loan('tie-b-1', 'tie-b', '103', date(2026, 1, 8), date(2026, 1, 25)),
            Loan('tie-a-1', 'tie-a', '104', date(2026, 1, 9), date(2026, 1, 26)),
            Loan('current-1', 'current', '105', date(2026, 1, 31)),
            Loan('on-time-1', 'on-time', '110', date(2026, 1, 7), date(2026, 1, 21)),
            Loan('previous-1', 'previous-only', '106', date(2025, 12, 30), date(2026, 1, 15)),
            Loan('next-1', 'next-month', '107', date(2026, 2, 1)),
        ]
    )
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 2, 1))
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert list(csv.reader(StringIO(output.getvalue()))) == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['alpha', '2', '2', '125'],
        ['tie-a', '1', '1', '75'],
        ['tie-b', '1', '1', '75'],
        ['zeta', '1', '1', '75'],
        ['current', '1', '0', '0'],
        ['on-time', '1', '0', '0'],
    ]


@pytest.mark.django_db
def test_monthly_report_uses_december_when_run_on_january_first(monkeypatch):
    Loan.objects.all().delete()
    Loan.objects.bulk_create(
        [
            Loan('december-first', 'december', '108', date(2025, 12, 1), date(2025, 12, 15)),
            Loan('december-1', 'december', '108', date(2025, 12, 31), date(2025, 12, 31)),
            Loan('previous-year-1', 'previous-year', '109', date(2024, 12, 1)),
            Loan('january-1', 'january', '110', date(2026, 1, 1), date(2026, 1, 1)),
        ]
    )
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 1, 1))
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert list(csv.reader(StringIO(output.getvalue()))) == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['december', '2', '0', '0'],
    ]


@pytest.mark.django_db
def test_monthly_report_includes_first_day_of_a_regular_month(monkeypatch):
    Loan.objects.all().delete()
    Loan.objects.bulk_create(
        [
            Loan('march-1', 'march', '111', date(2026, 3, 31)),
            Loan('april-1', 'april', '112', date(2026, 4, 1), date(2026, 4, 15)),
            Loan('may-1', 'may', '113', date(2026, 5, 1)),
        ]
    )
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 5, 1))
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert list(csv.reader(StringIO(output.getvalue()))) == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['april', '1', '0', '0'],
    ]
