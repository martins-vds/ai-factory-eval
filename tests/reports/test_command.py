import csv
from datetime import date
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_aggregates_previous_calendar_month():
    Loan.objects.all().delete()
    Loan.objects.bulk_create(
        [
            Loan(
                id='A-old',
                member='alpha',
                isbn='1',
                lent_on=date(2026, 1, 1),
                returned_on=date(2026, 3, 25),
            ),
            Loan(
                id='A-new',
                member='alpha',
                isbn='2',
                lent_on=date(2026, 3, 1),
                returned_on=date(2026, 3, 18),
            ),
            Loan(
                id='B',
                member='bravo',
                isbn='3',
                lent_on=date(2026, 3, 5),
                returned_on=date(2026, 3, 22),
            ),
            Loan(id='C', member='charlie', isbn='4', lent_on=date(2026, 3, 10)),
            Loan(
                id='D',
                member='delta',
                isbn='5',
                lent_on=date(2026, 3, 12),
                returned_on=date(2026, 3, 26),
            ),
            Loan(
                id='E',
                member='echo',
                isbn='6',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 2, 20),
            ),
            Loan(
                id='F',
                member='foxtrot',
                isbn='7',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 3, 20),
            ),
            Loan(id='F-new', member='foxtrot', isbn='9', lent_on=date(2026, 3, 10)),
            Loan(id='G', member='golf', isbn='8', lent_on=date(2026, 4, 1)),
        ]
    )
    output = StringIO()

    with patch('src.loans.clock.timezone.localdate', return_value=date(2026, 4, 1)):
        call_command('monthly_report', stdout=output)

    assert list(csv.reader(output.getvalue().splitlines())) == [
        ['member_id', 'loans_started', 'late_returns', 'total_late_fees_cents'],
        ['alpha', '1', '2', '1075'],
        ['foxtrot', '1', '1', '825'],
        ['bravo', '1', '1', '75'],
        ['charlie', '1', '0', '0'],
        ['delta', '1', '0', '0'],
    ]


@pytest.mark.django_db
def test_monthly_report_handles_january_year_boundary():
    Loan.objects.all().delete()
    Loan.objects.bulk_create(
        [
            Loan(
                id='previous-year',
                member='winter',
                isbn='1',
                lent_on=date(2025, 11, 1),
                returned_on=date(2025, 12, 2),
            ),
            Loan(id='winter-start', member='winter', isbn='3', lent_on=date(2025, 12, 31)),
            Loan(id='december', member='new-reader', isbn='2', lent_on=date(2025, 12, 31)),
        ]
    )
    output = StringIO()

    with patch('src.loans.clock.timezone.localdate', return_value=date(2026, 1, 1)):
        call_command('monthly_report', stdout=output)

    assert list(csv.reader(output.getvalue().splitlines())) == [
        ['member_id', 'loans_started', 'late_returns', 'total_late_fees_cents'],
        ['winter', '1', '1', '425'],
        ['new-reader', '1', '0', '0'],
    ]
