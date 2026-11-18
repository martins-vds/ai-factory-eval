from dataclasses import dataclass
from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command

from src.loans.models import Loan
from src.reports.services import MonthlyReportApplication


@dataclass(frozen=True)
class ReportLoan:
    id: str
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None = None


class ReportLoanRepository:
    def __init__(self, loans):
        self.loans = loans
        self.started_range = None
        self.returned_range = None

    def started_between(self, start, end):
        self.started_range = (start, end)
        return [loan for loan in self.loans if start <= loan.lent_on < end]

    def returned_between(self, start, end):
        self.returned_range = (start, end)
        return [
            loan
            for loan in self.loans
            if loan.returned_on is not None and start <= loan.returned_on < end
        ]


class FixedClock:
    def __init__(self, today):
        self.value = today

    def today(self):
        return self.value


class FeeCalculator:
    def __init__(self, fees):
        self.fees = fees
        self.loan_ids = []

    def fee_for(self, loan_id):
        self.loan_ids.append(loan_id)
        return self.fees.get(loan_id)


@dataclass(frozen=True)
class ReportFee:
    amount_cents: int


def test_report_use_case_uses_previous_calendar_month_and_omits_nonstarters():
    repository = ReportLoanRepository(
        [
            ReportLoan('D1', 'december', date(2026, 12, 1), date(2026, 12, 15)),
            ReportLoan('D2', 'december', date(2026, 12, 31), date(2027, 1, 14)),
            ReportLoan('J1', 'january', date(2027, 1, 1), date(2027, 1, 15)),
            ReportLoan(
                'N1',
                'no-start',
                date(2026, 11, 1),
                date(2026, 11, 20),
                date(2026, 12, 10),
            ),
        ]
    )
    fees = FeeCalculator({'N1': ReportFee(25)})
    application = MonthlyReportApplication(
        repository,
        FixedClock(date(2027, 1, 1)),
        fees,
    )

    rows = application.rows()

    assert repository.started_range == (date(2026, 12, 1), date(2027, 1, 1))
    assert repository.returned_range == (date(2026, 12, 1), date(2027, 1, 1))
    assert [(row.member_id, row.loans_started) for row in rows] == [('december', 2)]
    assert fees.loan_ids == []


def test_report_use_case_counts_only_late_returns_and_sums_their_fees():
    repository = ReportLoanRepository(
        [
            ReportLoan('S1', 'member', date(2026, 2, 1), date(2026, 2, 10)),
            ReportLoan(
                'ON_TIME',
                'member',
                date(2026, 1, 1),
                date(2026, 2, 10),
                date(2026, 2, 10),
            ),
            ReportLoan(
                'LATE_1',
                'member',
                date(2026, 1, 1),
                date(2026, 2, 10),
                date(2026, 2, 11),
            ),
            ReportLoan(
                'LATE_2',
                'member',
                date(2026, 1, 1),
                date(2026, 2, 12),
                date(2026, 2, 20),
            ),
        ]
    )
    fees = FeeCalculator(
        {
            'ON_TIME': ReportFee(999),
            'LATE_1': ReportFee(25),
            'LATE_2': ReportFee(75),
        }
    )
    application = MonthlyReportApplication(
        repository,
        FixedClock(date(2026, 3, 1)),
        fees,
    )

    rows = application.rows()

    assert [(row.late_returns, row.late_fees_cents) for row in rows] == [(2, 100)]
    assert fees.loan_ids == ['LATE_1', 'LATE_2']


def test_report_use_case_sorts_by_fees_then_member_id():
    repository = ReportLoanRepository(
        [
            ReportLoan(f'S-{member}', member, date(2026, 2, 1), date(2026, 2, 10))
            for member in ('zoe', 'alice', 'bob', 'zero')
        ]
        + [
            ReportLoan(
                f'R-{member}',
                member,
                date(2026, 1, 1),
                date(2026, 2, 10),
                date(2026, 2, 11),
            )
            for member in ('zoe', 'alice', 'bob')
        ]
    )
    fees = FeeCalculator(
        {
            'R-zoe': ReportFee(75),
            'R-alice': ReportFee(75),
            'R-bob': ReportFee(100),
        }
    )
    application = MonthlyReportApplication(
        repository,
        FixedClock(date(2026, 3, 1)),
        fees,
    )

    rows = application.rows()

    assert [row.member_id for row in rows] == ['bob', 'alice', 'zoe', 'zero']


@pytest.mark.django_db
def test_monthly_report_summarizes_the_previous_calendar_month(monkeypatch):
    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2026, 3, 1))
    Loan.objects.bulk_create(
        [
            Loan(
                id='R1',
                member='zoe',
                isbn='1',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 2, 20),
            ),
            Loan(
                id='R2',
                member='zoe',
                isbn='2',
                lent_on=date(2026, 1, 20),
                returned_on=date(2026, 2, 10),
            ),
            Loan(
                id='R3',
                member='zoe',
                isbn='3',
                lent_on=date(2026, 2, 25),
                returned_on=date(2026, 3, 5),
            ),
            Loan(
                id='R4',
                member='alice',
                isbn='4',
                lent_on=date(2026, 2, 1),
                returned_on=date(2026, 2, 16),
            ),
            Loan(id='R5', member='bob', isbn='5', lent_on=date(2026, 2, 2)),
            Loan(
                id='R6',
                member='carol',
                isbn='6',
                lent_on=date(2026, 1, 1),
                returned_on=date(2026, 2, 20),
            ),
            Loan(id='R7', member='zoe', isbn='7', lent_on=date(2026, 1, 31)),
            Loan(id='R8', member='zoe', isbn='8', lent_on=date(2026, 3, 1)),
        ]
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\n'
        'zoe,2,2,300\n'
        'alice,1,1,0\n'
        'bob,1,0,0\n'
    )


@pytest.mark.django_db
def test_monthly_report_previous_month_crosses_the_year_boundary(monkeypatch):
    monkeypatch.setattr('src.loans.clock.timezone.localdate', lambda: date(2027, 1, 1))
    Loan.objects.bulk_create(
        [
            Loan(id='R9', member='december', isbn='9', lent_on=date(2026, 12, 31)),
            Loan(id='R10', member='january', isbn='10', lent_on=date(2027, 1, 1)),
        ]
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert output.getvalue() == (
        'member_id,loans_started,late_returns,late_fees_cents\ndecember,1,0,0\n'
    )
