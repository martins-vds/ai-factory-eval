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
    ]


@pytest.mark.django_db
def test_monthly_report_uses_december_when_run_on_january_first(monkeypatch):
    Loan.objects.all().delete()
    Loan.objects.bulk_create(
        [
            Loan('december-1', 'december', '108', date(2025, 12, 31)),
            Loan('january-1', 'january', '109', date(2026, 1, 1)),
        ]
    )
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 1, 1))
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert list(csv.reader(StringIO(output.getvalue()))) == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['december', '1', '0', '0'],
    ]
