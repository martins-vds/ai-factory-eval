from dataclasses import dataclass
from datetime import date, timedelta

import pytest

from src.fees.services import FeeApplication


@dataclass
class Loan:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loans):
        self.loans = loans

    def find(self, loan_id):
        return self.loans.get(loan_id)


class FixedClock:
    def today(self):
        return date(2026, 11, 22)


class PaymentGateway:
    def __init__(self):
        self.loan_ids = []

    def charge(self, loan_id):
        self.loan_ids.append(loan_id)
        return None


@pytest.mark.parametrize(
    ('late_days', 'expected_cents'),
    [
        (-1, 0),
        (0, 0),
        (2, 0),
        (3, 75),
        (19, 475),
        (296, 1000),
    ],
)
def test_late_fee_obeys_grace_period_daily_rate_and_cap(late_days, expected_cents):
    loan = Loan('L1', date(2026, 11, 22) - timedelta(days=late_days))
    application = FeeApplication(LoanRepository({'L1': loan}), FixedClock(), PaymentGateway())

    fee = application.late_fee_for('L1')

    assert fee.days_late == max(0, late_days)
    assert fee.cents == expected_cents


def test_late_fee_uses_return_date_instead_of_current_date():
    loan = Loan('L1', date(2026, 11, 19), returned_on=date(2026, 11, 21))
    application = FeeApplication(LoanRepository({'L1': loan}), FixedClock(), PaymentGateway())

    fee = application.late_fee_for('L1')

    assert fee.days_late == 2
    assert fee.cents == 0


def test_late_fee_returns_none_for_an_unknown_loan():
    application = FeeApplication(LoanRepository({}), FixedClock(), PaymentGateway())

    assert application.late_fee_for('missing') is None


def test_payment_does_not_call_gateway_for_an_unknown_loan():
    gateway = PaymentGateway()
    application = FeeApplication(LoanRepository({}), FixedClock(), gateway)

    assert application.pay('missing') is None
    assert gateway.loan_ids == []
