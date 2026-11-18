from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command

from src.loans.models import Loan


def create_loan(loan_id, member, lent_on, returned_on=None):
    return Loan.objects.create(
        id=loan_id,
        member=member,
        isbn='123',
        lent_on=lent_on,
        returned_on=returned_on,
    )


@pytest.mark.django_db
def test_monthly_report_aggregates_previous_month_loans(monkeypatch):
    Loan.objects.all().delete()
    create_loan('LL05-01', 'alice', date(2026, 5, 3))
    create_loan('LL05-02', 'alice', date(2026, 3, 1), date(2026, 5, 1))
    create_loan('LL05-03', 'bob', date(2026, 5, 2), date(2026, 5, 16))
    create_loan('LL05-04', 'bob', date(2026, 5, 3), date(2026, 5, 20))
    create_loan('LL05-05', 'carol', date(2026, 5, 4), date(2026, 5, 19))
    create_loan('LL05-06', 'dave', date(2026, 5, 31), date(2026, 6, 1))
    create_loan('LL05-07', 'only-returned', date(2026, 3, 1), date(2026, 5, 1))
    create_loan('LL05-08', 'june', date(2026, 6, 1))
    create_loan('LL05-11', 'alice', date(2026, 5, 3), date(2026, 5, 20))
    create_loan('LL05-12', 'bob', date(2026, 5, 4), date(2026, 5, 19))

    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2026, 6, 1))
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'alice,2,2,1075\n'
        'bob,3,2,75\n'
        'carol,1,1,0\n'
        'dave,1,0,0\n'
    )


@pytest.mark.django_db
def test_monthly_report_prior_month_window_crosses_year_boundary(monkeypatch):
    Loan.objects.all().delete()
    create_loan('LL05-9', 'december', date(2025, 12, 31))
    create_loan('LL05-10', 'january', date(2026, 1, 1))
    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2026, 1, 1))
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\ndecember,1,0,0\n'
    )
