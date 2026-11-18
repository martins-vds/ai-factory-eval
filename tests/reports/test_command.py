from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_command_reads_postgres_for_the_local_prior_month(monkeypatch):
    Loan.objects.create(
        id='R1',
        member='report-member',
        isbn='123',
        lent_on=date(2026, 12, 1),
        returned_on=date(2026, 12, 18),
    )
    monkeypatch.setattr('src.reports.clock.timezone.localdate', lambda: date(2027, 1, 1))
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == 'report-member;1;1;75\n'
