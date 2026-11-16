from datetime import date

import pytest
from django.core.management import call_command

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_aggregates_activity_and_sorts_by_fees(capsys):
    Loan.objects.all().delete()
    Loan.objects.bulk_create(
        [
            Loan('L1', 'alpha', '1', date(2026, 2, 1), date(2026, 3, 1)),
            Loan('L2', 'alpha', '2', date(2026, 3, 31)),
            Loan('L3', 'beta', '3', date(2026, 2, 15), date(2026, 3, 5)),
            Loan('L4', 'beta', '4', date(2026, 3, 2)),
            Loan('L5', 'gamma, guest', '5', date(2026, 2, 15), date(2026, 3, 5)),
            Loan('L6', 'gamma, guest', '6', date(2026, 3, 1)),
            Loan('L7', 'delta', '7', date(2026, 2, 15), date(2026, 3, 3)),
            Loan('L8', 'delta', '8', date(2026, 3, 1)),
            Loan('L9', 'epsilon', '9', date(2026, 3, 1)),
            Loan('L10', 'zeta', '10', date(2026, 3, 31), date(2026, 4, 1)),
            Loan('L11', 'return-only', '11', date(2026, 2, 15), date(2026, 3, 5)),
            Loan('L12', 'outside', '12', date(2026, 2, 1), date(2026, 4, 1)),
        ]
    )

    call_command('monthly_report', month='2026-03')

    assert capsys.readouterr().out == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'alpha,1,1,350\n'
        'beta,1,1,100\n'
        '"gamma, guest",1,1,100\n'
        'delta,1,1,0\n'
        'epsilon,1,0,0\n'
        'zeta,1,0,0\n'
    )
