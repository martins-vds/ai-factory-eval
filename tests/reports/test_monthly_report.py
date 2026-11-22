from dataclasses import dataclass
from datetime import date, timedelta
from io import StringIO

import pytest

from src.reports.services import MonthlyReportApplication


@dataclass(frozen=True)
class LoanRecord:
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def for_period(self, start_on, end_on):
        return [
            loan
            for loan in self.loans
            if start_on <= loan.lent_on < end_on
            or loan.returned_on is not None
            and start_on <= loan.returned_on < end_on
        ]


class FixedClock:
    def __init__(self, today):
        self.value = today

    def today(self):
        return self.value


def report_rows(application):
    return [
        (row.member_id, row.loans_started, row.late_returns, row.late_fees_cents)
        for row in application.generate_previous_month_report()
    ]


def test_monthly_report_aggregates_prior_month_and_orders_members():
    loans = [
        LoanRecord('B', date(2028, 2, 1), date(2028, 2, 15), date(2028, 2, 18)),
        LoanRecord('B', date(2028, 1, 31), date(2028, 2, 14), date(2028, 2, 17)),
        LoanRecord('B', date(2028, 2, 29), date(2028, 3, 14), date(2028, 3, 14)),
        LoanRecord('A', date(2028, 2, 2), date(2028, 2, 16), date(2028, 2, 19)),
        LoanRecord('Z', date(2028, 2, 10), date(2028, 2, 24), date(2028, 2, 27)),
        LoanRecord('C', date(2028, 2, 1), date(2028, 2, 15), date(2028, 2, 15)),
        LoanRecord('OLD', date(2028, 1, 1), date(2028, 1, 15), date(2028, 2, 18)),
        LoanRecord('END', date(2028, 3, 1), date(2028, 3, 15), date(2028, 3, 18)),
    ]
    application = MonthlyReportApplication(LoanRepository(loans), FixedClock(date(2028, 3, 1)))

    assert report_rows(application) == [
        ('B', 2, 2, 150),
        ('A', 1, 1, 75),
        ('Z', 1, 1, 75),
        ('C', 1, 0, 0),
    ]


def test_monthly_report_uses_previous_december_at_year_boundary():
    loans = [
        LoanRecord('PREV', date(2027, 12, 31), date(2028, 1, 14)),
        LoanRecord('DEC-FIRST', date(2028, 12, 1), date(2028, 12, 15)),
        LoanRecord('DEC', date(2028, 12, 31), date(2029, 1, 14)),
        LoanRecord('JAN', date(2029, 1, 1), date(2029, 1, 15)),
    ]
    application = MonthlyReportApplication(LoanRepository(loans), FixedClock(date(2029, 1, 1)))

    assert report_rows(application) == [('DEC', 1, 0, 0), ('DEC-FIRST', 1, 0, 0)]


@pytest.mark.parametrize(
    ('due_on', 'returned_on', 'expected_fee_cents'),
    [
        (date(2028, 1, 31), date(2028, 2, 1), 0),
        (date(2028, 1, 31), date(2028, 2, 2), 0),
        (date(2028, 1, 31), date(2028, 2, 3), 75),
        (date(2028, 1, 1), date(2028, 2, 20), 1000),
    ],
)
def test_monthly_report_calculates_late_fees_in_cents(due_on, returned_on, expected_fee_cents):
    loans = [
        LoanRecord('M', date(2028, 2, 1), date(2028, 2, 15)),
        LoanRecord('M', due_on - timedelta(days=14), due_on, returned_on),
    ]
    application = MonthlyReportApplication(LoanRepository(loans), FixedClock(date(2028, 3, 1)))

    assert report_rows(application) == [('M', 1, 1, expected_fee_cents)]


@pytest.mark.django_db
def test_monthly_report_command_reads_postgres_and_writes_csv(monkeypatch):
    from django.core.management import call_command

    from src.loans.clock import SystemClock
    from src.loans.models import Loan

    as_of = date(2099, 3, 1)
    monkeypatch.setattr(SystemClock, 'today', lambda self: as_of)
    Loan.objects.create(
        id='REPORT-1',
        member='member,1',
        isbn='123',
        lent_on=date(2099, 2, 1),
        returned_on=date(2099, 2, 18),
    )
    Loan.objects.create(
        id='REPORT-2',
        member='member,1',
        isbn='456',
        lent_on=date(2099, 1, 31),
        returned_on=date(2099, 2, 17),
    )
    Loan.objects.create(
        id='REPORT-3',
        member='next-month',
        isbn='789',
        lent_on=date(2099, 3, 1),
        returned_on=date(2099, 3, 18),
    )
    Loan.objects.create(
        id='REPORT-4',
        member='no-start',
        isbn='012',
        lent_on=date(2099, 1, 1),
        returned_on=date(2099, 2, 18),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n"member,1",1,2,150\n'
    )
