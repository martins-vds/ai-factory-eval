from datetime import UTC, date, datetime, timedelta
from datetime import timezone as dt_timezone
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_aggregates_previous_month_and_sorts_members(monkeypatch):
    Loan.objects.bulk_create(
        [
            Loan(
                id='LL05-0',
                member='m1',
                isbn='0',
                lent_on=date(2024, 12, 1),
                returned_on=date(2024, 12, 15),
            ),
            Loan(
                id='LL05-8',
                member='m0',
                isbn='8',
                lent_on=date(2024, 12, 1),
            ),
            Loan(
                id='LL05-9',
                member='m0',
                isbn='9',
                lent_on=date(2024, 10, 1),
                returned_on=date(2024, 12, 31),
            ),
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
                id='LL05-11',
                member='m1',
                isbn='11',
                lent_on=date(2024, 11, 10),
                returned_on=date(2024, 12, 2),
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
                id='LL05-12',
                member='m2',
                isbn='12',
                lent_on=date(2024, 12, 1),
                returned_on=date(2024, 12, 18),
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
            Loan(
                id='LL05-10',
                member='m6',
                isbn='10',
                lent_on=date(2024, 12, 1),
                returned_on=date(2024, 12, 17),
            ),
            Loan(
                id='LL05-13',
                member='m6',
                isbn='13',
                lent_on=date(2024, 12, 2),
                returned_on=date(2024, 12, 17),
            ),
        ]
    )
    monkeypatch.setattr(
        'django.utils.timezone.now',
        lambda: datetime(2024, 12, 31, 12, tzinfo=UTC),
    )
    output = StringIO()

    with timezone.override(dt_timezone(timedelta(hours=14))):
        call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'm0,1,1,1000\n'
        'm1,2,2,600\n'
        'm2,3,2,175\n'
        'm3,1,1,100\n'
        'm5,1,0,0\n'
        'm6,2,2,0\n'
    )
