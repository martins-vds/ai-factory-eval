import csv
from datetime import UTC, date, datetime
from io import StringIO

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_summarizes_previous_month_started_loans_in_fee_order(monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2024, 3, 1))
    Loan.objects.bulk_create(
        [
            Loan(
                id='R1',
                member='alpha',
                isbn='1',
                lent_on=date(2024, 2, 1),
                returned_on=date(2024, 2, 18),
            ),
            Loan(
                id='R2',
                member='alpha',
                isbn='2',
                lent_on=date(2024, 2, 2),
                returned_on=date(2024, 2, 19),
            ),
            Loan(
                id='R3',
                member='alpha',
                isbn='3',
                lent_on=date(2024, 2, 3),
            ),
            Loan(
                id='R4',
                member='zeta',
                isbn='4',
                lent_on=date(2024, 2, 1),
                returned_on=date(2024, 2, 18),
            ),
            Loan(
                id='R5',
                member='beta',
                isbn='5',
                lent_on=date(2024, 2, 4),
                returned_on=date(2024, 2, 18),
            ),
            Loan(
                id='R6',
                member='zed',
                isbn='6',
                lent_on=date(2024, 2, 1),
                returned_on=date(2024, 2, 17),
            ),
            Loan(
                id='R7',
                member='outside',
                isbn='7',
                lent_on=date(2024, 1, 31),
                returned_on=date(2024, 2, 20),
            ),
            Loan(
                id='R8',
                member='outside',
                isbn='8',
                lent_on=date(2024, 3, 1),
                returned_on=date(2024, 3, 20),
            ),
            Loan(
                id='R9',
                member='alpha',
                isbn='9',
                lent_on=date(2023, 8, 1),
                returned_on=date(2024, 2, 20),
            ),
        ]
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    rows = list(csv.DictReader(output.getvalue().splitlines()))
    assert rows == [
        {
            'member_id': 'alpha',
            'loans_started': '3',
            'loans_returned_late': '3',
            'total_late_fees_cents': '1150',
        },
        {
            'member_id': 'zeta',
            'loans_started': '1',
            'loans_returned_late': '1',
            'total_late_fees_cents': '75',
        },
        {
            'member_id': 'beta',
            'loans_started': '1',
            'loans_returned_late': '0',
            'total_late_fees_cents': '0',
        },
        {
            'member_id': 'zed',
            'loans_started': '1',
            'loans_returned_late': '1',
            'total_late_fees_cents': '0',
        },
    ]


@pytest.mark.django_db
@override_settings(TIME_ZONE='America/Los_Angeles')
def test_monthly_report_uses_default_timezone_for_month_boundary(monkeypatch):
    monkeypatch.setattr(
        timezone,
        'now',
        lambda: datetime(2024, 3, 1, 7, 30, tzinfo=UTC),
    )
    Loan.objects.bulk_create(
        [
            Loan(id='R10', member='january', isbn='10', lent_on=date(2024, 1, 31)),
            Loan(id='R11', member='february', isbn='11', lent_on=date(2024, 2, 1)),
        ]
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    rows = list(csv.DictReader(output.getvalue().splitlines()))
    assert rows == [
        {
            'member_id': 'january',
            'loans_started': '1',
            'loans_returned_late': '0',
            'total_late_fees_cents': '0',
        },
    ]
