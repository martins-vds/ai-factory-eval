import csv
from dataclasses import dataclass
from datetime import date
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan as LoanModel
from src.reports.repository import DjangoMonthlyReportLoanRepository
from src.reports.services import MonthlyReportApplication, MonthlyReportRow


@dataclass
class Loan:
    id: str
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans
        self.period = None

    def started_in_period(self, start, end):
        self.period = start, end
        return self.loans


class FeeCalculator:
    def __init__(self, fees):
        self.fees = fees

    def fee_for(self, loan_id):
        return self.fees[loan_id]


@dataclass
class Fee:
    amount_cents: int


def test_monthly_report_aggregates_prior_month_and_orders_members_by_fees_then_id():
    repository = LoanRepository(
        [
            Loan('L1', 'zara', date(2026, 2, 1), date(2026, 2, 15), date(2026, 2, 18)),
            Loan('L2', 'amy', date(2026, 2, 2), date(2026, 2, 16), date(2026, 2, 19)),
            Loan('L3', 'dee', date(2026, 2, 3), date(2026, 2, 17), date(2026, 2, 20)),
            Loan('L6', 'zara', date(2026, 2, 4), date(2026, 2, 18), date(2026, 2, 21)),
            Loan('L7', 'zara', date(2026, 2, 5), date(2026, 2, 19), date(2026, 2, 19)),
        ]
    )
    application = MonthlyReportApplication(
        repository,
        FeeCalculator({'L1': Fee(1000), 'L2': Fee(75), 'L3': Fee(75), 'L6': Fee(75), 'L7': Fee(0)}),
    )

    report = application.monthly_report_for(date(2026, 3, 1))

    assert repository.period == (date(2026, 2, 1), date(2026, 3, 1))
    assert report == [
        MonthlyReportRow('zara', 3, 2, 1075),
        MonthlyReportRow('amy', 1, 1, 75),
        MonthlyReportRow('dee', 1, 1, 75),
    ]


def test_monthly_report_for_january_uses_december_of_the_previous_year():
    repository = LoanRepository([])
    application = MonthlyReportApplication(repository, FeeCalculator({}))

    report = application.monthly_report_for(date(2026, 1, 1))

    assert repository.period == (date(2025, 12, 1), date(2026, 1, 1))
    assert report == []


@pytest.mark.django_db
def test_monthly_report_application_excludes_loans_outside_the_previous_month():
    LoanModel.objects.create(
        id='LL05-before',
        member='before',
        isbn='1',
        lent_on=date(2026, 1, 31),
    )
    LoanModel.objects.create(
        id='LL05-start',
        member='qualifying',
        isbn='2',
        lent_on=date(2026, 2, 1),
    )
    LoanModel.objects.create(
        id='LL05-last',
        member='qualifying',
        isbn='3',
        lent_on=date(2026, 2, 28),
    )
    LoanModel.objects.create(
        id='LL05-end',
        member='after',
        isbn='4',
        lent_on=date(2026, 3, 1),
    )
    application = MonthlyReportApplication(
        DjangoMonthlyReportLoanRepository(),
        FeeCalculator({'LL05-start': Fee(0), 'LL05-last': Fee(0)}),
    )

    report = application.monthly_report_for(date(2026, 3, 1))

    assert report == [MonthlyReportRow('qualifying', 2, 0, 0)]


@pytest.mark.django_db
def test_monthly_report_command_outputs_only_loans_started_in_the_prior_month(monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2026, 3, 1))
    LoanModel.objects.create(
        id='LL05-1',
        member='zara',
        isbn='1',
        lent_on=date(2026, 2, 1),
        returned_on=date(2026, 2, 18),
    )
    LoanModel.objects.create(
        id='LL05-2',
        member='amy',
        isbn='2',
        lent_on=date(2026, 2, 2),
        returned_on=date(2026, 2, 19),
    )
    LoanModel.objects.create(
        id='LL05-3',
        member='outside',
        isbn='3',
        lent_on=date(2026, 1, 31),
        returned_on=date(2026, 2, 20),
    )
    LoanModel.objects.create(
        id='LL05-4',
        member='outside',
        isbn='4',
        lent_on=date(2026, 3, 1),
    )
    LoanModel.objects.create(
        id='LL05-5',
        member='open',
        isbn='5',
        lent_on=date(2026, 2, 1),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert list(csv.reader(output.getvalue().splitlines())) == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['open', '1', '0', '350'],
        ['amy', '1', '1', '75'],
        ['zara', '1', '1', '75'],
    ]
