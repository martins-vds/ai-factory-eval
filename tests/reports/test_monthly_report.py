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
    create_loan('O3', 'Zed', date(2026, 10, 3), date(2026, 10, 20))
    create_loan('O7', 'Eve', date(2026, 10, 5), date(2026, 10, 31))
    create_loan('O8', 'Grace', date(2026, 10, 1), date(2026, 10, 17))
    create_loan('O9', 'Due', date(2026, 10, 1), date(2026, 10, 15))
    create_loan('O10', 'Zed', date(2026, 10, 4), date(2026, 10, 21))
    create_loan('O4', 'Zed', date(2026, 10, 31))
    create_loan('O5', 'Excluded', date(2026, 9, 30), date(2026, 10, 31))
    create_loan('O6', 'Excluded', date(2026, 11, 1))

    output = StringIO()
    call_command('monthly_report', '--month', '2026-10', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'Eve,1,1,300\n'
        'Zed,3,2,150\n'
        'Bex,1,1,125\n'
        'Ada,1,1,100\n'
        'Due,1,0,0\n'
        'Grace,1,1,0\n'
    )


@pytest.mark.django_db
def test_monthly_report_defaults_to_the_month_before_the_server_date(monkeypatch):
    create_loan('O1', 'Reader', date(2026, 11, 1))
    create_loan('O2', 'Reader', date(2026, 11, 20))
    monkeypatch.setattr(
        'src.reports.management.commands.monthly_report.timezone.localdate',
        lambda: date(2026, 12, 1),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\nReader,2,0,375\n'
    )
