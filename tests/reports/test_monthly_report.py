import csv
from datetime import date
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_lists_monthly_members_with_late_returns_and_fees():
    Loan.objects.bulk_create(
        [
            Loan(
                id='L10',
                member='alpha',
                isbn='10',
                lent_on=date(2026, 1, 1),
                returned_on=date(2026, 2, 3),
            ),
            Loan(
                id='L11',
                member='alpha',
                isbn='11',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 2, 14),
            ),
            Loan(
                id='L12',
                member='beta',
                isbn='12',
                lent_on=date(2026, 1, 31),
                returned_on=date(2026, 2, 17),
            ),
            Loan(
                id='L13',
                member='beta',
                isbn='13',
                lent_on=date(2026, 2, 28),
            ),
            Loan(id='L14', member='gamma', isbn='14', lent_on=date(2026, 2, 1)),
            Loan(id='L15', member='delta', isbn='15', lent_on=date(2026, 2, 28)),
            Loan(
                id='L16',
                member='not-in-report',
                isbn='16',
                lent_on=date(2026, 1, 1),
                returned_on=date(2026, 1, 20),
            ),
            Loan(id='L17', member='next-month', isbn='17', lent_on=date(2026, 3, 1)),
        ]
    )
    output = StringIO()

    with patch('django.utils.timezone.localdate', return_value=date(2026, 3, 1)):
        call_command('monthly_report', stdout=output)

    assert list(csv.reader(StringIO(output.getvalue()))) == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['alpha', '1', '1', '475'],
        ['beta', '1', '1', '75'],
        ['delta', '1', '0', '0'],
        ['gamma', '1', '0', '0'],
    ]
