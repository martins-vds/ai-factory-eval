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
            Loan('R-ALPHA', 'Alpha', '1', date(2026, 2, 3), date(2026, 2, 23)),
            Loan('R-BETA-1', 'Beta', '2', date(2026, 2, 4), date(2026, 2, 19)),
            Loan('R-BETA-2', 'Beta', '3', date(2026, 2, 5), date(2026, 2, 23)),
            Loan('R-BETA-3', 'Beta', '7', date(2026, 2, 6), date(2026, 2, 22)),
            Loan('R-CY', 'Cy', '4', date(2026, 2, 6), date(2026, 2, 24)),
            Loan('R-OPEN', 'Open', '5', date(2026, 2, 20)),
            Loan('R-OLD', 'Old', '6', date(2026, 1, 31), date(2026, 2, 28)),
        ]
    )
    output = StringIO()

    with patch('django.utils.timezone.localdate', return_value=date(2026, 3, 1)):
        call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,total_late_fees_cents\n'
        'Alpha,1,1,150\n'
        'Beta,3,3,100\n'
        'Cy,1,1,100\n'
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
