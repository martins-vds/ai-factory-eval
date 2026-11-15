import csv
from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_groups_month_activity_and_sorts_by_fees(monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 4, 1))
    loans = [
        ('L10', 'zed', date(2026, 3, 1), date(2026, 3, 18)),
        ('L11', 'zed', date(2026, 2, 1), date(2026, 3, 1)),
        ('L12', 'zed', date(2026, 2, 1), date(2026, 4, 1)),
        ('L13', 'amy', date(2026, 3, 31), None),
        ('L14', 'bob', date(2026, 3, 1), date(2026, 3, 17)),
        ('L15', 'cara', date(2026, 3, 1), None),
        ('L16', 'hidden', date(2026, 2, 1), date(2026, 3, 1)),
        ('L17', 'outside', date(2026, 4, 1), None),
    ]
    for loan_id, member, lent_on, returned_on in loans:
        Loan.objects.create(
            id=loan_id,
            member=member,
            isbn='123',
            lent_on=lent_on,
            returned_on=returned_on,
        )

    output = StringIO()
    call_command('monthly_report', stdout=output, verbosity=0)

    assert list(csv.reader(StringIO(output.getvalue()))) == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['zed', '1', '2', '425'],
        ['amy', '1', '0', '0'],
        ['bob', '1', '1', '0'],
        ['cara', '1', '0', '0'],
    ]
