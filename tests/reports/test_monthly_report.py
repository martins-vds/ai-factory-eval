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
        ('monthly-report-b-on-time', 'B', 5, 14),
        ('monthly-report-c-waived', 'C', 6, 16),
        ('monthly-report-one-day', 'One Day', 7, 15),
        ('monthly-report-z', 'Z', 8, 17),
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
        'B,3,2,150\n'
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


@pytest.mark.django_db
def test_monthly_report_application_waives_first_two_days_of_lateness():
    class JanuaryFirst:
        def today(self):
            return date(2099, 1, 1)

    Loan.objects.create(
        id='monthly-report-one-day-late',
        member='One',
        isbn='isbn',
        lent_on=date(2098, 12, 1),
        returned_on=date(2098, 12, 16),
    )
    Loan.objects.create(
        id='monthly-report-two-days-late',
        member='Two',
        isbn='isbn',
        lent_on=date(2098, 12, 2),
        returned_on=date(2098, 12, 18),
    )
    Loan.objects.create(
        id='monthly-report-three-days-late',
        member='Three',
        isbn='isbn',
        lent_on=date(2098, 12, 3),
        returned_on=date(2098, 12, 20),
    )

    report = MonthlyReportApplication(DjangoMonthlyReportRepository(), JanuaryFirst())

    assert report.generate() == [
        MonthlyReportRow('Three', 1, 1, 75),
        MonthlyReportRow('One', 1, 1, 0),
        MonthlyReportRow('Two', 1, 1, 0),
    ]


@pytest.mark.django_db
def test_monthly_report_application_orders_by_fees_then_member_id():
    class JanuaryFirst:
        def today(self):
            return date(2099, 1, 1)

    Loan.objects.create(
        id='monthly-report-order-z',
        member='Z',
        isbn='isbn',
        lent_on=date(2098, 12, 1),
        returned_on=date(2098, 12, 18),
    )
    Loan.objects.create(
        id='monthly-report-order-a',
        member='A',
        isbn='isbn',
        lent_on=date(2098, 12, 2),
        returned_on=date(2098, 12, 19),
    )
    Loan.objects.create(
        id='monthly-report-order-high',
        member='High',
        isbn='isbn',
        lent_on=date(2098, 12, 3),
        returned_on=date(2098, 12, 23),
    )

    report = MonthlyReportApplication(DjangoMonthlyReportRepository(), JanuaryFirst())

    assert report.generate() == [
        MonthlyReportRow('High', 1, 1, 150),
        MonthlyReportRow('A', 1, 1, 75),
        MonthlyReportRow('Z', 1, 1, 75),
    ]


@pytest.mark.django_db
def test_monthly_report_caps_each_loan_fee():
    class FebruaryTwentyEighth:
        def today(self):
            return date(2099, 2, 28)

    Loan.objects.create(
        id='monthly-report-capped',
        member='Member',
        isbn='isbn',
        lent_on=date(2099, 1, 1),
    )

    report = MonthlyReportApplication(DjangoMonthlyReportRepository(), FebruaryTwentyEighth())

    assert report.generate() == [MonthlyReportRow('Member', 1, 0, 1000)]
