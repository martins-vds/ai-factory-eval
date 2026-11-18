from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_summarizes_the_previous_calendar_month(monkeypatch):
    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2026, 3, 1))
    Loan.objects.bulk_create(
        [
            Loan(
                id='R1',
                member='zoe',
                isbn='1',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 2, 20),
            ),
            Loan(
                id='R2',
                member='zoe',
                isbn='2',
                lent_on=date(2026, 1, 20),
                returned_on=date(2026, 2, 10),
            ),
            Loan(
                id='R3',
                member='zoe',
                isbn='3',
                lent_on=date(2026, 2, 25),
                returned_on=date(2026, 3, 5),
            ),
            Loan(
                id='R4',
                member='alice',
                isbn='4',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 2, 16),
            ),
            Loan(id='R5', member='bob', isbn='5', lent_on=date(2026, 2, 2)),
            Loan(
                id='R6',
                member='carol',
                isbn='6',
                lent_on=date(2026, 1, 1),
                returned_on=date(2026, 2, 20),
            ),
            Loan(id='R7', member='zoe', isbn='7', lent_on=date(2026, 1, 31)),
            Loan(id='R8', member='zoe', isbn='8', lent_on=date(2026, 3, 1)),
        ]
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'zoe,2,2,300\n'
        'alice,1,1,0\n'
        'bob,1,0,0\n'
    )


@pytest.mark.django_db
def test_monthly_report_previous_month_crosses_the_year_boundary(monkeypatch):
    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2027, 1, 1))
    Loan.objects.bulk_create(
        [
            Loan(id='R9', member='december', isbn='9', lent_on=date(2026, 12, 31)),
            Loan(id='R10', member='january', isbn='10', lent_on=date(2027, 1, 1)),
        ]
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\ndecember,1,0,0\n'
    )
