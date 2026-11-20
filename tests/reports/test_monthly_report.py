import csv
from dataclasses import dataclass
from datetime import date, timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from src.fees.services import FeeApplication
from src.loans.models import Loan as DjangoLoan
from src.reports.services import MonthlyReportApplication, MonthlyReportRow


@dataclass
class Loan:
    id: str
    member: str
    lent_on: date
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def all(self):
        return self.loans

    def find(self, loan_id):
        return next((loan for loan in self.loans if loan.id == loan_id), None)


class Clock:
    def today(self):
        return date(2024, 3, 1)


class PaymentGateway:
    def charge(self, loan_id):
        raise AssertionError('monthly reports must not charge the payment gateway')


def test_report_summarizes_previous_month_activity_and_sorts_by_fees_then_member():
    loans = [
        Loan('L1', 'z-member', date(2024, 2, 1), date(2024, 2, 15), date(2024, 2, 19)),
        Loan('L2', 'z-member', date(2024, 1, 4), date(2024, 1, 18), date(2024, 2, 1)),
        Loan('L3', 'a-member', date(2024, 2, 29), date(2024, 3, 14)),
        Loan('L4', 'b-member', date(2024, 2, 1), date(2024, 2, 15), date(2024, 2, 17)),
        Loan('L5', 'b-member', date(2024, 1, 10), date(2024, 1, 24), date(2024, 3, 1)),
        Loan('L6', 'omitted', date(2024, 1, 10), date(2024, 1, 24), date(2024, 2, 20)),
        Loan('L7', 'march-only', date(2024, 3, 1), date(2024, 3, 15)),
    ]
    repository = LoanRepository(loans)
    application = MonthlyReportApplication(
        repository,
        Clock(),
        FeeApplication(repository, Clock(), PaymentGateway()),
    )

    report = application.generate()

    assert report == [
        MonthlyReportRow('z-member', loans_started=1, late_returns=2, late_fees_cents=450),
        MonthlyReportRow('a-member', loans_started=1, late_returns=0, late_fees_cents=0),
        MonthlyReportRow('b-member', loans_started=1, late_returns=1, late_fees_cents=0),
    ]


@pytest.mark.django_db
def test_monthly_report_command_reads_postgres_and_writes_csv():
    today = timezone.localdate()
    current_month_start = today.replace(day=1)
    previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    lent_on = previous_month_start
    returned_on = lent_on + timedelta(days=20)
    DjangoLoan.objects.create(
        id='monthly-report-command-test',
        member='report-command-member',
        isbn='report-command-isbn',
        lent_on=lent_on,
        returned_on=returned_on,
    )
    output = StringIO()

    call_command('monthly_report', stdout=output)

    rows = list(csv.reader(StringIO(output.getvalue())))
    assert rows[0] == ['member_id', 'loans_started', 'late_returns', 'late_fees_cents']
    assert ['report-command-member', '1', '1', '150'] in rows
