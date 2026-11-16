from datetime import date
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_lists_previous_month_member_totals_in_specified_order():
    Loan.objects.bulk_create(
        [
            Loan('R-STILL-OUT', 'Still out', '8', date(2026, 2, 1)),
            Loan('R-ALPHA', 'Alpha', '1', date(2026, 2, 3), date(2026, 2, 23)),
            Loan('R-BETA-1', 'Beta', '2', date(2026, 2, 4), date(2026, 2, 19)),
            Loan('R-BETA-2', 'Beta', '3', date(2026, 2, 5), date(2026, 2, 23)),
            Loan('R-BETA-3', 'Beta', '7', date(2026, 2, 6), date(2026, 2, 23)),
            Loan('R-BETA-4', 'Beta', '11', date(2026, 2, 7), date(2026, 2, 23)),
            Loan('R-CY', 'Cy', '4', date(2026, 2, 6), date(2026, 2, 27)),
            Loan('R-DUE', 'Due', '9', date(2026, 2, 2), date(2026, 2, 16)),
            Loan('R-OPEN', 'Open', '5', date(2026, 2, 20)),
            Loan('R-OLD', 'Old', '6', date(2026, 1, 31), date(2026, 2, 28)),
            Loan('R-MARCH', 'March', '10', date(2026, 3, 1)),
        ]
    )
    output = StringIO()

    with patch('django.utils.timezone.localdate', return_value=date(2026, 3, 1)):
        call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,total_late_fees_cents\n'
        'Still out,1,0,350\n'
        'Beta,4,4,175\n'
        'Cy,1,1,175\n'
        'Alpha,1,1,150\n'
        'Due,1,0,0\n'
        'Open,1,0,0\n'
    )


@pytest.mark.django_db
def test_monthly_report_includes_december_when_run_on_january_first():
    Loan.objects.bulk_create(
        [
            Loan('R-DEC', 'December', '1', date(2026, 12, 10), date(2027, 1, 1)),
            Loan('R-JAN', 'January', '2', date(2027, 1, 1)),
        ]
    )
    output = StringIO()

    with patch('django.utils.timezone.localdate', return_value=date(2027, 1, 1)):
        call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,total_late_fees_cents\nDecember,1,1,200\n'
    )


@pytest.mark.django_db
def test_monthly_report_caps_each_loan_fee():
    Loan.objects.create(id='R-CAP', member='Cap', isbn='1', lent_on=date(2026, 3, 1))
    output = StringIO()

    with patch('django.utils.timezone.localdate', return_value=date(2026, 4, 30)):
        call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,total_late_fees_cents\nCap,1,0,1000\n'
    )
