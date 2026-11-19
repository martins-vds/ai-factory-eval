from dataclasses import dataclass
from datetime import date, timedelta

import pytest

from src.fees.services import FeeApplication, PaymentApplication


@dataclass
class LoanRecord:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loan=None):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan and self.loan.id == loan_id else None


class FixedClock:
    def __init__(self, today):
        self.current_date = today

    def today(self):
        return self.current_date


class RecordingGateway:
    def __init__(self):
        self.loan_ids = []

    def charge(self, loan_id):
        self.loan_ids.append(loan_id)


@pytest.mark.parametrize(
    ('late_days', 'fee_cents'),
    [(0, 0), (2, 0), (3, 75), (50, 1000)],
)
def test_fee_application_applies_waiver_daily_rate_and_cap(late_days, fee_cents):
    due_on = date(2026, 1, 16)
    loan = LoanRecord('L1', due_on, due_on + timedelta(days=late_days))
    application = FeeApplication(LoanRepository(loan), FixedClock(date(2026, 3, 7)))

    fee = application.calculate('L1')

    assert fee.loan_id == 'L1'
    assert fee.due_on == due_on
    assert fee.late_days == late_days
    assert fee.fee_cents == fee_cents


def test_fee_application_uses_today_for_an_unreturned_loan():
    due_on = date(2026, 1, 16)
    application = FeeApplication(
        LoanRepository(LoanRecord('L1', due_on)),
        FixedClock(due_on + timedelta(days=4)),
    )

    fee = application.calculate('L1')

    assert fee.late_days == 4
    assert fee.fee_cents == 100


def test_fee_application_returns_none_for_an_unknown_loan():
    application = FeeApplication(LoanRepository(), FixedClock(date(2026, 3, 7)))

    assert application.calculate('missing') is None


def test_payment_application_does_not_call_gateway_for_an_unknown_loan():
    gateway = RecordingGateway()
    application = PaymentApplication(LoanRepository(), gateway)

    assert application.pay('missing') is None
    assert gateway.loan_ids == []
