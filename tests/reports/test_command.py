from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_command_outputs_previous_month_csv(monkeypatch, django_assert_num_queries):
    Loan.objects.create(
        id='LL05-1',
        member='ada, smith',
        isbn='123',
        lent_on=date(2026, 2, 2),
        returned_on=date(2026, 2, 21),
    )
    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2026, 3, 1))
    output = StringIO()

    with django_assert_num_queries(1):
        call_command('monthly_report', stdout=output)

    assert (
        output.getvalue()
        == 'member_id,loans_started,loans_returned_late,total_late_fees_cents\n"ada, smith",1,1,125\n'
    )
