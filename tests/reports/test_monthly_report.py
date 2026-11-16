from datetime import date

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_defaults_to_previous_month_in_default_timezone(monkeypatch, capsys):
    Loan.objects.all().delete()
    Loan.objects.bulk_create(
        [
            Loan('L3', 'previous', '3', date(2025, 12, 1)),
            Loan('L1', 'previous', '1', date(2025, 12, 31)),
            Loan('L2', 'current', '2', date(2026, 1, 1)),
        ]
    )
    default_timezone = timezone.get_default_timezone()
    requested_timezones = []

    def localdate(*, timezone):
        requested_timezones.append(timezone)
        return date(2026, 1, 1)

    monkeypatch.setattr('src.reports.services.timezone.localdate', localdate)

    call_command('monthly_report')

    assert requested_timezones == [default_timezone]
    assert capsys.readouterr().out == (
        'member_id,loans_started,late_returns,late_fees_cents\nprevious,2,0,0\n'
    )


def test_monthly_report_rejects_invalid_month():
    with pytest.raises(CommandError, match='month must use YYYY-MM format'):
        call_command('monthly_report', month='2026-13')


@pytest.mark.django_db
def test_monthly_report_aggregates_activity_and_sorts_by_fees(capsys):
    Loan.objects.all().delete()
    Loan.objects.bulk_create(
        [
            Loan('L13', 'cap', '13', date(2026, 2, 1), date(2026, 3, 31)),
            Loan('L14', 'cap', '14', date(2026, 3, 1)),
            Loan('L1', 'alpha', '1', date(2026, 2, 1), date(2026, 3, 1)),
            Loan('L2', 'alpha', '2', date(2026, 3, 31)),
            Loan('L15', 'alpha', '15', date(2026, 2, 1), date(2026, 3, 5)),
            Loan('L16', 'alpha', '16', date(2026, 3, 15)),
            Loan('L3', 'beta', '3', date(2026, 2, 15), date(2026, 3, 5)),
            Loan('L4', 'beta', '4', date(2026, 3, 2)),
            Loan('L5', 'gamma, guest', '5', date(2026, 2, 15), date(2026, 3, 5)),
            Loan('L6', 'gamma, guest', '6', date(2026, 3, 1)),
            Loan('L7', 'delta', '7', date(2026, 2, 15), date(2026, 3, 3)),
            Loan('L8', 'delta', '8', date(2026, 3, 1)),
            Loan('L9', 'epsilon', '9', date(2026, 3, 1), date(2026, 3, 15)),
            Loan('L10', 'zeta', '10', date(2026, 3, 31), date(2026, 4, 1)),
            Loan('L11', 'return-only', '11', date(2026, 2, 15), date(2026, 3, 5)),
            Loan('L12', 'outside', '12', date(2026, 2, 1), date(2026, 4, 1)),
        ]
    )

    call_command('monthly_report', month='2026-03')

    assert capsys.readouterr().out == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'cap,1,1,1000\n'
        'alpha,2,2,800\n'
        'beta,1,1,100\n'
        '"gamma, guest",1,1,100\n'
        'delta,1,1,0\n'
        'epsilon,1,0,0\n'
        'zeta,1,0,0\n'
    )
