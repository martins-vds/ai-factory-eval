from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_summarizes_previous_month_by_member(monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))
    Loan.objects.create(
        id='LL05-1',
        member='beta',
        isbn='1',
        lent_on=date(2026, 2, 1),
        returned_on=date(2026, 2, 20),
    )
    Loan.objects.create(
        id='LL05-2',
        member='alpha',
        isbn='2',
        lent_on=date(2026, 2, 1),
        returned_on=date(2026, 2, 17),
    )
    Loan.objects.create(
        id='LL05-3',
        member='zeta',
        isbn='3',
        lent_on=date(2026, 2, 15),
    )
    Loan.objects.create(
        id='LL05-4',
        member='outside',
        isbn='4',
        lent_on=date(2026, 3, 1),
    )
    Loan.objects.create(
        id='LL05-5',
        member='beta',
        isbn='5',
        lent_on=date(2026, 2, 10),
        returned_on=date(2026, 2, 28),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'beta,2,2,225\n'
        'alpha,1,1,0\n'
        'zeta,1,0,0\n'
    )


@pytest.mark.django_db
def test_monthly_report_uses_previous_month_across_year_boundary(monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2099, 1, 1))
    Loan.objects.create(
        id='LL05-6',
        member='winter',
        isbn='6',
        lent_on=date(2098, 12, 31),
    )
    Loan.objects.create(
        id='LL05-7',
        member='current',
        isbn='7',
        lent_on=date(2099, 1, 1),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'winter,1,0,0\n'
    )
