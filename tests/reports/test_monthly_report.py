import csv
from dataclasses import dataclass
from datetime import date, timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.loans.models import Loan as LoanModel
from src.reports.services import MonthlyReport, MonthlyReportRow


@dataclass
class Loan:
    id: str
    member: str
    lent_on: date
    returned_on: date | None = None

    @property
    def due_on(self):
        return self.lent_on + timedelta(days=14)


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def all(self):
        return self.loans


class Clock:
    def __init__(self, today=date(2026, 3, 1)):
        self.value = today

    def today(self):
        return self.value


def test_monthly_report_summarizes_prior_month_loan_activity():
    application = MonthlyReport(
        LoanRepository(
            [
                Loan('L1', 'ada', date(2026, 2, 1), date(2026, 2, 20)),
                Loan('L2', 'ada', date(2026, 2, 10)),
                Loan('L3', 'bea', date(2026, 2, 2), date(2026, 2, 17)),
                Loan('L4', 'cora', date(2026, 2, 3), date(2026, 2, 18)),
                Loan('L7', 'dave', date(2026, 2, 1), date(2026, 2, 15)),
                Loan('L5', 'outside', date(2026, 1, 31), date(2026, 2, 25)),
                Loan('L6', 'future', date(2026, 3, 1)),
            ]
        ),
        Clock(),
    )

    rows = application.generate()

    assert rows == [
        MonthlyReportRow('ada', loans_started=2, late_returns=1, late_fees_cents=250),
        MonthlyReportRow('bea', loans_started=1, late_returns=1, late_fees_cents=0),
        MonthlyReportRow('cora', loans_started=1, late_returns=1, late_fees_cents=0),
        MonthlyReportRow('dave', loans_started=1, late_returns=0, late_fees_cents=0),
    ]


def test_monthly_report_handles_year_boundary_and_month_edges():
    application = MonthlyReport(
        LoanRepository(
            [
                Loan('L1', 'december', date(2026, 12, 1), date(2026, 12, 20)),
                Loan('L2', 'november', date(2026, 11, 30), date(2026, 12, 20)),
                Loan('L3', 'january', date(2027, 1, 1)),
            ]
        ),
        Clock(date(2027, 1, 1)),
    )

    rows = application.generate()

    assert rows == [
        MonthlyReportRow('december', loans_started=1, late_returns=1, late_fees_cents=125),
    ]


@pytest.mark.django_db
def test_monthly_report_command_outputs_sorted_csv(monkeypatch):
    monkeypatch.setattr(timezone, 'localdate', lambda: date(2027, 1, 1))
    LoanModel.objects.create(
        id='RPT1',
        member='beta',
        isbn='123',
        lent_on=date(2026, 12, 1),
        returned_on=date(2026, 12, 20),
    )
    LoanModel.objects.create(
        id='RPT2',
        member='alpha',
        isbn='456',
        lent_on=date(2026, 12, 2),
        returned_on=date(2026, 12, 17),
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    assert list(csv.reader(output.getvalue().splitlines())) == [
        ['member_id', 'loans_started', 'late_returns', 'late_fees_cents'],
        ['beta', '1', '1', '125'],
        ['alpha', '1', '1', '0'],
    ]
