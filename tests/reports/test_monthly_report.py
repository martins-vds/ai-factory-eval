import csv
from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_groups_activity_by_member_and_orders_by_late_fees(monkeypatch):
    Loan.objects.bulk_create(
        [
            Loan(
                id='R1',
                member='Alpha',
                isbn='1',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 2, 18),
            ),
            Loan(
                id='R2',
                member='Alpha',
                isbn='2',
                lent_on=date(2026, 1, 1),
                returned_on=date(2026, 2, 17),
            ),
            Loan(
                id='R3',
                member='Alpha',
                isbn='3',
                lent_on=date(2026, 2, 4),
            ),
            Loan(
                id='R4',
                member='Beta',
                isbn='4',
                lent_on=date(2026, 1, 1),
                returned_on=date(2026, 2, 17),
            ),
            Loan(
                id='R5',
                member='Gamma',
                isbn='5',
                lent_on=date(2026, 1, 1),
                returned_on=date(2026, 2, 17),
            ),
            Loan(
                id='R6',
                member='New member',
                isbn='6',
                lent_on=date(2026, 2, 3),
            ),
            Loan(
                id='R7',
                member='Outside',
                isbn='7',
                lent_on=date(2026, 1, 1),
                returned_on=date(2026, 1, 10),
            ),
        ]
    )
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert list(csv.reader(output.getvalue().splitlines())) == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['Alpha', '2', '2', '900'],
        ['Beta', '0', '1', '825'],
        ['Gamma', '0', '1', '825'],
        ['New member', '1', '0', '0'],
    ]
