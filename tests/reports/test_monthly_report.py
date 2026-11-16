import csv
from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan


def create_loan(loan_id, member, lent_on, returned_on=None):
    return Loan.objects.create(
        id=loan_id,
        member=member,
        isbn='9780000000000',
        lent_on=lent_on,
        returned_on=returned_on,
    )


@pytest.mark.django_db
def test_monthly_report_summarizes_prior_month_returns_and_orders_by_fees_then_member(
    monkeypatch,
):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))
    create_loan('old-a', 'alpha', date(2026, 1, 10), date(2026, 2, 20))
    create_loan('start-a', 'alpha', date(2026, 2, 3))
    create_loan('old-b', 'bravo', date(2026, 1, 10), date(2026, 2, 16))
    create_loan('start-b', 'bravo', date(2026, 2, 11))
    create_loan('old-c', 'beta', date(2026, 1, 20), date(2026, 2, 4))
    create_loan('start-c', 'beta', date(2026, 2, 12))
    create_loan('start-d', 'delta', date(2026, 2, 13))
    create_loan('old-e', 'echo', date(2026, 1, 10), date(2026, 3, 1))
    create_loan('start-e', 'echo', date(2026, 2, 14))
    create_loan('only-old', 'excluded', date(2026, 1, 10), date(2026, 2, 20))
    create_loan('next-month', 'excluded-next', date(2026, 3, 1))

    output = StringIO()
    call_command('monthly_report', stdout=output)

    assert list(csv.reader(StringIO(output.getvalue()))) == [
        ['member_id', 'loans_started', 'loans_returned_late', 'total_late_fees_cents'],
        ['alpha', '1', '1', '675'],
        ['bravo', '1', '1', '575'],
        ['beta', '1', '0', '0'],
        ['delta', '1', '0', '0'],
        ['echo', '1', '0', '0'],
    ]
