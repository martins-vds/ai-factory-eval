from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_summarizes_previous_month_loans(monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 12, 1))
    Loan.objects.bulk_create(
        [
            Loan(
                id='R-active',
                member='Active',
                isbn='1',
                lent_on=date(2026, 11, 1),
            ),
            Loan(
                id='R-apple',
                member='Apple',
                isbn='2',
                lent_on=date(2026, 11, 1),
                returned_on=date(2026, 11, 20),
            ),
            Loan(
                id='R-mango-late',
                member='Mango',
                isbn='3',
                lent_on=date(2026, 11, 1),
                returned_on=date(2026, 11, 19),
            ),
            Loan(
                id='R-mango-current',
                member='Mango',
                isbn='4',
                lent_on=date(2026, 11, 20),
            ),
            Loan(
                id='R-zed',
                member='Zed',
                isbn='5',
                lent_on=date(2026, 11, 1),
                returned_on=date(2026, 11, 19),
            ),
            Loan(
                id='R-grace',
                member='Grace',
                isbn='6',
                lent_on=date(2026, 11, 1),
                returned_on=date(2026, 11, 17),
            ),
            Loan(
                id='R-before',
                member='Before',
                isbn='7',
                lent_on=date(2026, 10, 31),
                returned_on=date(2026, 12, 1),
            ),
            Loan(
                id='R-after',
                member='After',
                isbn='8',
                lent_on=date(2026, 12, 1),
            ),
        ]
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member,loans_started,late_returns,late_fees_cents\n'
        'Active,1,0,400\n'
        'Apple,1,1,125\n'
        'Mango,2,1,100\n'
        'Zed,1,1,100\n'
        'Grace,1,1,0\n'
    )


@pytest.mark.django_db
def test_monthly_report_previous_month_window_crosses_year_boundary(monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2027, 1, 1))
    Loan.objects.create(
        id='R-december',
        member='December',
        isbn='1',
        lent_on=date(2026, 12, 31),
    )
    Loan.objects.create(
        id='R-november',
        member='November',
        isbn='2',
        lent_on=date(2026, 11, 30),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member,loans_started,late_returns,late_fees_cents\n'
        'December,1,0,0\n'
    )
