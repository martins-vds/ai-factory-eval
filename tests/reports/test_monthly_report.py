from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_summarizes_the_previous_month(monkeypatch):
    monkeypatch.setattr('django.utils.timezone.localdate', lambda: date(2026, 3, 1))
    Loan.objects.bulk_create(
        [
            Loan('L10', 'alpha', '1', date(2026, 2, 1), date(2026, 2, 18)),
            Loan('L11', 'alpha', '2', date(2026, 2, 2), date(2026, 2, 20)),
            Loan('L12', 'beta', '3', date(2026, 2, 3), date(2026, 2, 17)),
            Loan('L13', 'beta', '4', date(2026, 2, 10)),
            Loan('L14', 'zoe', '5', date(2026, 2, 5), date(2026, 2, 20)),
            Loan('L15', 'aardvark', '6', date(2026, 2, 6), date(2026, 2, 22)),
            Loan('L16', 'old-only', '7', date(2026, 1, 1), date(2026, 2, 20)),
            Loan('L17', 'march-only', '8', date(2026, 3, 1)),
        ]
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member,loans_started,late_returns,late_fees_cents\n'
        'alpha,2,2,175\n'
        'beta,2,0,100\n'
        'aardvark,1,1,0\n'
        'zoe,1,1,0\n'
    )
