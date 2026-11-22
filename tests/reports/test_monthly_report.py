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
            Loan(
                id='R8',
                member='Zeta',
                isbn='8',
                lent_on=date(2026, 1, 1),
                returned_on=date(2026, 2, 25),
            ),
            Loan(
                id='R9',
                member='Month end',
                isbn='9',
                lent_on=date(2026, 2, 28),
            ),
            Loan(
                id='R10',
                member='Next month',
                isbn='10',
                lent_on=date(2026, 3, 1),
            ),
            Loan(
                id='R11',
                member='Grace',
                isbn='11',
                lent_on=date(2026, 1, 20),
                returned_on=date(2026, 2, 5),
            ),
            Loan(
                id='R12',
                member='On-time return',
                isbn='12',
                lent_on=date(2026, 1, 20),
                returned_on=date(2026, 2, 1),
            ),
            Loan(id='R13', member='Beta', isbn='13', lent_on=date(2026, 2, 2)),
            Loan(id='R14', member='Gamma', isbn='14', lent_on=date(2026, 2, 2)),
            Loan(id='R15', member='Zeta', isbn='15', lent_on=date(2026, 2, 3)),
            Loan(id='R16', member='Grace', isbn='16', lent_on=date(2026, 2, 4)),
            Loan(id='R17', member='On-time return', isbn='17', lent_on=date(2026, 2, 4)),
            Loan(
                id='R18',
                member='Return only',
                isbn='18',
                lent_on=date(2026, 1, 1),
                returned_on=date(2026, 2, 17),
            ),
        ]
    )
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert list(csv.reader(output.getvalue().splitlines())) == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['Zeta', '1', '1', '1000'],
        ['Alpha', '2', '2', '900'],
        ['Beta', '1', '1', '825'],
        ['Gamma', '1', '1', '825'],
        ['Grace', '1', '1', '0'],
        ['Month end', '1', '0', '0'],
        ['New member', '1', '0', '0'],
        ['On-time return', '1', '0', '0'],
    ]
