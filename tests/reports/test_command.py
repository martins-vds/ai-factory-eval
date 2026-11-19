from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan

pytestmark = pytest.mark.django_db


def test_monthly_report_command_outputs_previous_month_as_csv(django_assert_num_queries):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    previous_month_start = (month_start - timedelta(days=1)).replace(day=1)
    lent_on = previous_month_start
    due_on = lent_on + timedelta(days=14)
    Loan.objects.create(
        id='L-report',
        member='Member, One',
        isbn='123',
        lent_on=lent_on,
        returned_on=due_on + timedelta(days=3),
    )
    Loan.objects.create(
        id='L-report-2',
        member='Member, One',
        isbn='124',
        lent_on=lent_on,
        returned_on=due_on,
    )
    Loan.objects.create(
        id='L-before',
        member='Excluded',
        isbn='456',
        lent_on=previous_month_start - timedelta(days=1),
    )
    Loan.objects.create(
        id='L-current',
        member='Excluded',
        isbn='789',
        lent_on=month_start,
    )
    output = StringIO()

    with django_assert_num_queries(1):
        call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n"Member, One",2,1,75\n'
    )
