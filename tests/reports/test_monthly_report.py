from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_summarizes_previous_month_by_fees_and_member(monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 4, 1))
    Loan.objects.create(
        id='REPORT-01',
        member='a-member',
        isbn='1',
        lent_on=date(2026, 3, 1),
        returned_on=date(2026, 3, 26),
    )
    Loan.objects.create(
        id='REPORT-02',
        member='a-member',
        isbn='2',
        lent_on=date(2026, 3, 4),
        returned_on=None,
    )
    Loan.objects.create(
        id='REPORT-03',
        member='b-member',
        isbn='3',
        lent_on=date(2026, 3, 1),
        returned_on=date(2026, 3, 18),
    )
    Loan.objects.create(
        id='REPORT-04',
        member='c-member',
        isbn='4',
        lent_on=date(2026, 3, 2),
        returned_on=date(2026, 3, 19),
    )
    Loan.objects.create(
        id='REPORT-05',
        member='no-fee',
        isbn='5',
        lent_on=date(2026, 3, 3),
        returned_on=date(2026, 3, 17),
    )
    Loan.objects.create(
        id='REPORT-06',
        member='outside-month',
        isbn='6',
        lent_on=date(2026, 2, 28),
        returned_on=date(2026, 3, 31),
    )
    Loan.objects.create(
        id='REPORT-07',
        member='outside-month',
        isbn='7',
        lent_on=date(2026, 4, 1),
        returned_on=None,
    )
    Loan.objects.create(
        id='REPORT-08',
        member='two-days-late',
        isbn='8',
        lent_on=date(2026, 3, 3),
        returned_on=date(2026, 3, 19),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'a-member,2,1,625\n'
        'b-member,1,1,75\n'
        'c-member,1,1,75\n'
        'no-fee,1,0,0\n'
        'two-days-late,1,1,0\n'
    )


@pytest.mark.django_db
def test_monthly_report_csv_escapes_member_ids(monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 4, 1))
    Loan.objects.create(
        id='REPORT-CSV',
        member='reader, "one"',
        isbn='978',
        lent_on=date(2026, 3, 1),
        returned_on=date(2026, 3, 15),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        '"reader, ""one""",1,0,0\n'
    )
