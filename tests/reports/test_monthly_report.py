import csv
import io
from datetime import date
from unittest.mock import patch

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
def test_monthly_report_groups_monthly_loans_and_sorts_by_fees_then_member():
    create_loan('R1', 'alpha', date(2026, 3, 1))
    create_loan('R2', 'alpha', date(2026, 3, 30), date(2026, 3, 31))
    create_loan('R3', 'zeta', date(2026, 3, 1), date(2026, 3, 18))
    create_loan('R4', 'beta', date(2026, 3, 1), date(2026, 3, 17))
    create_loan('R5', 'reader, "one"\ncontinued', date(2026, 3, 31))
    create_loan('R6', 'alpha', date(2026, 2, 28), date(2026, 3, 20))

    output = io.StringIO()

    call_command('monthly_report', '--month', '2026-03', stdout=output)

    rows = list(csv.reader(io.StringIO(output.getvalue(), newline='')))
    assert rows == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['alpha', '2', '0', '425'],
        ['zeta', '1', '1', '75'],
        ['beta', '1', '1', '0'],
        ['reader, "one"\ncontinued', '1', '0', '0'],
    ]


@pytest.mark.django_db
def test_monthly_report_defaults_to_previous_month_in_server_timezone():
    create_loan('R1', 'march reader', date(2026, 3, 15))
    create_loan('R2', 'february reader', date(2026, 2, 15))
    create_loan('R3', 'april reader', date(2026, 4, 1))
    output = io.StringIO()

    with patch('django.utils.timezone.localdate', return_value=date(2026, 4, 1)):
        call_command('monthly_report', stdout=output)

    rows = list(csv.reader(io.StringIO(output.getvalue(), newline='')))
    assert rows == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['march reader', '1', '0', '75'],
    ]
