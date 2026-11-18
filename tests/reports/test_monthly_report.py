from datetime import date, timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan
from src.reports.repository import DjangoMonthlyReportRepository
from src.reports.services import MonthlyReportApplication, MonthlyReportRow


@pytest.mark.django_db
def test_monthly_report_lists_member_totals_for_the_previous_month():
    month_start = timezone.localdate().replace(day=1)
    previous_month_start = (month_start - timedelta(days=1)).replace(day=1)

    loans = [
        ('monthly-report-a', 'A, Member', 2, 17),
        ('monthly-report-b-late', 'B', 3, 17),
        ('monthly-report-b-late-again', 'B', 4, 17),
        ('monthly-report-c-waived', 'C', 5, 16),
        ('monthly-report-one-day', 'One Day', 6, 15),
        ('monthly-report-z', 'Z', 7, 17),
        ('monthly-report-outside', 'Outside', -1, 17),
        (
            'monthly-report-current',
            'Current',
            (month_start - previous_month_start).days,
            14,
        ),
    ]
    for loan_id, member, lent_offset, return_offset in loans:
        lent_on = previous_month_start + timedelta(days=lent_offset)
        Loan.objects.create(
            id=loan_id,
            member=member,
            isbn='isbn',
            lent_on=lent_on,
            returned_on=lent_on + timedelta(days=return_offset),
        )

    output = StringIO()
    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'B,2,2,150\n'
        '"A, Member",1,1,75\n'
        'Z,1,1,75\n'
        'C,1,1,0\n'
        'One Day,1,1,0\n'
    )


@pytest.mark.django_db
def test_monthly_report_uses_calendar_months_and_counts_accrued_fees():
    class JanuaryFirst:
        def today(self):
            return date(2099, 1, 1)

    Loan.objects.create(
        id='monthly-report-open',
        member='Member',
        isbn='isbn',
        lent_on=date(2098, 12, 1),
    )
    Loan.objects.create(
        id='monthly-report-returned-late',
        member='Member',
        isbn='isbn',
        lent_on=date(2098, 12, 2),
        returned_on=date(2098, 12, 19),
    )
    Loan.objects.create(
        id='monthly-report-november',
        member='Outside',
        isbn='isbn',
        lent_on=date(2098, 11, 30),
    )

    report = MonthlyReportApplication(DjangoMonthlyReportRepository(), JanuaryFirst())

    assert report.generate() == [MonthlyReportRow('Member', 2, 1, 500)]
