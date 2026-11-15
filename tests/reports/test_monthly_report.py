from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan


@pytest.mark.django_db
def test_monthly_report_aggregates_previous_month_and_sorts_by_fees_then_member(
    monkeypatch,
):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))
    Loan.objects.bulk_create(
        [
            Loan(
                id='report-z-start-1',
                member='member-z',
                isbn='1',
                lent_on=date(2026, 2, 1),
            ),
            Loan(
                id='report-z-start-2',
                member='member-z',
                isbn='2',
                lent_on=date(2026, 2, 28),
            ),
            Loan(
                id='report-z-late',
                member='member-z',
                isbn='3',
                lent_on=date(2025, 12, 1),
                returned_on=date(2026, 2, 20),
            ),
            Loan(
                id='report-z-late-2',
                member='member-z',
                isbn='4',
                lent_on=date(2025, 11, 1),
                returned_on=date(2026, 2, 21),
            ),
            Loan(
                id='report-a-late',
                member='member-a',
                isbn='5',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 2, 18),
            ),
            Loan(
                id='report-a-early',
                member='member-a',
                isbn='6',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 2, 14),
            ),
            Loan(
                id='report-b-late',
                member='member-b',
                isbn='7',
                lent_on=date(2026, 2, 3),
                returned_on=date(2026, 2, 20),
            ),
            Loan(
                id='report-c-late-within-grace',
                member='member-c',
                isbn='8',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 2, 16),
            ),
            Loan(
                id='report-d-start',
                member='member-d',
                isbn='9',
                lent_on=date(2026, 2, 5),
            ),
            Loan(
                id='report-d-return-on-first',
                member='member-d',
                isbn='10',
                lent_on=date(2025, 12, 1),
                returned_on=date(2026, 2, 1),
            ),
            Loan(
                id='report-e-late-two-days',
                member='member-e',
                isbn='11',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 2, 17),
            ),
            Loan(
                id='report-no-start',
                member='member-without-starts',
                isbn='12',
                lent_on=date(2026, 1, 1),
                returned_on=date(2026, 2, 20),
            ),
            Loan(
                id='report-a-after-window',
                member='member-a',
                isbn='13',
                lent_on=date(2025, 12, 1),
                returned_on=date(2026, 3, 1),
            ),
            Loan(
                id='report-start-after-window',
                member='member-outside-window',
                isbn='14',
                lent_on=date(2026, 3, 1),
            ),
        ]
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'member-z,2,2,2000\n'
        'member-d,1,1,1000\n'
        'member-a,2,1,75\n'
        'member-b,1,1,75\n'
        'member-c,1,1,0\n'
        'member-e,1,1,0\n'
    )
