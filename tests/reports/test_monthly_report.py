from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_summarizes_the_previous_month(monkeypatch):
    Loan.objects.bulk_create(
        [
            Loan(
                id='R1',
                member='alpha',
                isbn='1',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 2, 18),
            ),
            Loan(id='R2', member='alpha', isbn='2', lent_on=date(2026, 2, 10)),
            Loan(
                id='R8',
                member='alpha',
                isbn='8',
                lent_on=date(2026, 1, 30),
                returned_on=date(2026, 2, 20),
            ),
            Loan(
                id='R9',
                member='alpha',
                isbn='9',
                lent_on=date(2025, 11, 17),
                returned_on=date(2026, 2, 28),
            ),
            Loan(
                id='R10',
                member='alpha',
                isbn='10',
                lent_on=date(2026, 1, 15),
                returned_on=date(2026, 2, 1),
            ),
            Loan(
                id='R3',
                member='amy',
                isbn='3',
                lent_on=date(2026, 2, 3),
                returned_on=date(2026, 2, 17),
            ),
            Loan(
                id='R4',
                member='beta',
                isbn='4',
                lent_on=date(2026, 2, 4),
                returned_on=date(2026, 2, 18),
            ),
            Loan(
                id='R11',
                member='carol',
                isbn='11',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 2, 17),
            ),
            Loan(
                id='R5',
                member='mike',
                isbn='5',
                lent_on=date(2026, 2, 14),
                returned_on=date(2026, 3, 5),
            ),
            Loan(
                id='R6',
                member='old member',
                isbn='6',
                lent_on=date(2026, 1, 31),
                returned_on=date(2026, 2, 20),
            ),
            Loan(id='R7', member='upcoming', isbn='7', lent_on=date(2026, 3, 1)),
        ]
    )
    monkeypatch.setattr('src.reports.services.timezone.localdate', lambda: date(2026, 3, 1))
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'alpha,2,4,1325\n'
        'amy,1,0,0\n'
        'beta,1,0,0\n'
        'carol,1,1,0\n'
        'mike,1,0,0\n'
    )
