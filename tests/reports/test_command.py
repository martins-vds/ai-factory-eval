import csv
from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_command_prints_previous_month_rows_from_database():
    current_month = timezone.localdate().replace(day=1)
    previous_month = (current_month - timedelta(days=1)).replace(day=1)

    Loan.objects.create(
        id='LL05-high',
        member='ll05-high-member',
        isbn='high',
        lent_on=previous_month,
        returned_on=previous_month + timedelta(days=17),
    )
    Loan.objects.create(
        id='LL05-low',
        member='ll05-low-member',
        isbn='low',
        lent_on=previous_month + timedelta(days=1),
        returned_on=previous_month + timedelta(days=18),
    )
    Loan.objects.create(
        id='LL05-outside',
        member='ll05-outside-member',
        isbn='outside',
        lent_on=current_month,
        returned_on=current_month + timedelta(days=17),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    rows = list(csv.reader(StringIO(output.getvalue())))
    report = {row[0]: row[1:] for row in rows[1:]}
    assert rows[0] == [
        'member_id',
        'loans_started',
        'late_returns',
        'total_late_fees_cents',
    ]
    assert report['ll05-high-member'] == ['1', '1', '75']
    assert report['ll05-low-member'] == ['1', '1', '75']
    assert 'll05-outside-member' not in report
