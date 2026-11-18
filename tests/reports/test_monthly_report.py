import csv
from datetime import UTC, date, datetime
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from src.loans.models import Loan


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
        ['alpha', '2', '1', '125'],
        ['beta', '1', '1', '125'],
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
    ]
