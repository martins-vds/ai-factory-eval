from datetime import date, datetime, timezone
from io import StringIO

import pytest
from django.core.management import call_command

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_aggregates_previous_month_and_sorts_members(monkeypatch):
    Loan.objects.bulk_create(
        [
            Loan(
                id='LL05-1',
                member='m1',
                isbn='1',
                lent_on=date(2024, 12, 10),
            ),
            Loan(
                id='LL05-2',
                member='m1',
                isbn='2',
                lent_on=date(2024, 11, 1),
                returned_on=date(2024, 12, 1),
            ),
            Loan(
                id='LL05-3',
                member='m2',
                isbn='3',
                lent_on=date(2024, 12, 1),
                returned_on=date(2024, 12, 19),
            ),
            Loan(
                id='LL05-4',
                member='m2',
                isbn='4',
                lent_on=date(2024, 12, 20),
            ),
            Loan(
                id='LL05-5',
                member='m3',
                isbn='5',
                lent_on=date(2024, 12, 2),
                returned_on=date(2024, 12, 20),
            ),
            Loan(
                id='LL05-6',
                member='m4',
                isbn='6',
                lent_on=date(2024, 11, 1),
                returned_on=date(2024, 12, 2),
            ),
            Loan(
                id='LL05-7',
                member='m5',
                isbn='7',
                lent_on=date(2024, 12, 1),
                returned_on=date(2025, 1, 1),
            ),
        ]
    )
    monkeypatch.setattr(
        'django.utils.timezone.now',
        lambda: datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'm1,1,1,400\n'
        'm2,2,1,100\n'
        'm3,1,1,100\n'
        'm5,1,0,0\n'
    )
