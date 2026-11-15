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
def test_monthly_report_summarizes_the_previous_month_in_fee_then_member_order():
    create_loan('O1', 'Bex', date(2026, 10, 1), date(2026, 10, 20))
    create_loan('O2', 'Ada', date(2026, 10, 2), date(2026, 10, 20))
    create_loan('O3', 'Zed', date(2026, 10, 3), date(2026, 10, 18))
    create_loan('O4', 'Zed', date(2026, 10, 20))
    create_loan('O5', 'Excluded', date(2026, 9, 30), date(2026, 10, 31))
    create_loan('O6', 'Excluded', date(2026, 11, 1))

    output = StringIO()
    call_command('monthly_report', '--month', '2026-10', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'Bex,1,1,125\n'
        'Ada,1,1,100\n'
        'Zed,2,1,75\n'
    )


@pytest.mark.django_db
def test_monthly_report_defaults_to_the_month_before_the_server_date(monkeypatch):
    create_loan('O1', 'Reader', date(2026, 10, 1))
    monkeypatch.setattr(
        'src.reports.management.commands.monthly_report.timezone.localdate',
        lambda: date(2026, 11, 1),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'Reader,1,0,0\n'
    )
