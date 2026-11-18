from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.utils import timezone
import pytest

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_lists_member_totals_for_the_previous_month():
    month_start = timezone.localdate().replace(day=1)
    previous_month_start = (month_start - timedelta(days=1)).replace(day=1)

    loans = [
        ('monthly-report-a', 'A', 2, 17),
        ('monthly-report-b-late', 'B', 3, 17),
        ('monthly-report-b-on-time', 'B', 4, 14),
        ('monthly-report-c-waived', 'C', 5, 16),
        ('monthly-report-outside', 'Outside', -1, 17),
    ]
    for loan_id, member, lent_offset, return_offset in loans:
        lent_on = previous_month_start + timedelta(days=lent_offset)
        Loan.objects.create(
            id=loan_id,
            member=member,
            isbn='isbn',
            lent_on=lent_on,
            returned_on=lent_on + timedelta(days=return_offset),
        )

    output = StringIO()
    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'A,1,1,75\n'
        'B,2,1,75\n'
        'C,1,1,0\n'
    )
