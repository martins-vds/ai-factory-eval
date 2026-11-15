import csv
from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_lists_previous_month_activity_in_fee_order(monkeypatch):
    Loan.objects.all().delete()
    Loan.objects.bulk_create(
        [
            Loan(
                id='REPORT-1',
                member='ALPHA',
                isbn='1',
                lent_on=date(2025, 12, 10),
                returned_on=date(2025, 12, 27),
            ),
            Loan(
                id='REPORT-2',
                member='BETA',
                isbn='2',
                lent_on=date(2025, 12, 10),
                returned_on=date(2025, 12, 30),
            ),
            Loan(
                id='REPORT-3',
                member='ALPHA',
                isbn='3',
                lent_on=date(2025, 12, 12),
                returned_on=date(2025, 12, 26),
            ),
            Loan(
                id='REPORT-7',
                member='ALPHA',
                isbn='7',
                lent_on=date(2025, 12, 1),
                returned_on=date(2026, 1, 1),
            ),
            Loan(
                id='REPORT-4',
                member='GAMMA',
                isbn='4',
                lent_on=date(2025, 12, 11),
                returned_on=date(2025, 12, 28),
            ),
            Loan(
                id='REPORT-8',
                member='WAIVED',
                isbn='8',
                lent_on=date(2025, 12, 13),
                returned_on=date(2025, 12, 29),
            ),
            Loan(
                id='REPORT-5',
                member='OUTSIDE',
                isbn='5',
                lent_on=date(2025, 11, 30),
                returned_on=date(2025, 12, 31),
            ),
            Loan(id='REPORT-6', member='FUTURE', isbn='6', lent_on=date(2026, 1, 1)),
        ]
    )
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 1, 1))
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert list(csv.reader(StringIO(output.getvalue()))) == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['BETA', '1', '1', '150'],
        ['ALPHA', '3', '1', '75'],
        ['GAMMA', '1', '1', '75'],
        ['WAIVED', '1', '1', '0'],
    ]
