from datetime import date
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_summarizes_prior_month_started_loans_in_fee_order():
    Loan.objects.create(
        id='R1',
        member='beta',
        isbn='1',
        lent_on=date(2026, 10, 1),
        returned_on=date(2026, 10, 18),
    )
    Loan.objects.create(
        id='R2',
        member='beta',
        isbn='2',
        lent_on=date(2026, 10, 2),
    )
    Loan.objects.create(
        id='R3',
        member='alpha',
        isbn='3',
        lent_on=date(2026, 10, 1),
        returned_on=date(2026, 10, 16),
    )
    Loan.objects.create(
        id='R4',
        member='charlie',
        isbn='4',
        lent_on=date(2026, 10, 31),
    )
    Loan.objects.create(
        id='R5',
        member='outside',
        isbn='5',
        lent_on=date(2026, 9, 30),
        returned_on=date(2026, 10, 30),
    )
    Loan.objects.create(
        id='R6',
        member='current',
        isbn='6',
        lent_on=date(2026, 11, 1),
    )
    Loan.objects.create(
        id='R7',
        member='delta',
        isbn='7',
        lent_on=date(2026, 10, 1),
    )
    Loan.objects.create(
        id='R11',
        member='beta',
        isbn='11',
        lent_on=date(2026, 10, 3),
        returned_on=date(2026, 10, 19),
    )
    Loan.objects.create(
        id='R12',
        member='on_time',
        isbn='12',
        lent_on=date(2026, 10, 1),
        returned_on=date(2026, 10, 15),
    )
    output = StringIO()

    with patch('django.utils.timezone.localdate', return_value=date(2026, 11, 1)):
        call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,loans_returned_late,late_fees_cents\n'
        'beta,3,2,475\n'
        'delta,1,0,425\n'
        'alpha,1,1,0\n'
        'charlie,1,0,0\n'
        'on_time,1,0,0\n'
    )


@pytest.mark.django_db
def test_monthly_report_includes_previous_december_when_run_on_january_first():
    Loan.objects.create(
        id='R8',
        member='reader',
        isbn='8',
        lent_on=date(2026, 12, 10),
        returned_on=date(2026, 12, 28),
    )
    Loan.objects.create(
        id='R9',
        member='reader',
        isbn='9',
        lent_on=date(2026, 12, 31),
    )
    Loan.objects.create(
        id='R10',
        member='current',
        isbn='10',
        lent_on=date(2027, 1, 1),
    )
    output = StringIO()

    with patch('django.utils.timezone.localdate', return_value=date(2027, 1, 1)):
        call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,loans_returned_late,late_fees_cents\nreader,2,1,100\n'
    )
