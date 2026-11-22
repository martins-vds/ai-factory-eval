from dataclasses import dataclass
from datetime import date

import pytest

from src.fees.services import FeeApplication, PaymentApplication, PaymentResponse


@dataclass
class Loan:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, *loans):
        self.loans = {loan.id: loan for loan in loans}

    def find(self, loan_id):
        return self.loans.get(loan_id)


class FixedClock:
    def today(self):
        return date(2026, 1, 19)


class RecordingGateway:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def charge(self, loan_id):
        self.calls.append(loan_id)
        return self.response


def test_fee_calculation_charges_twenty_five_cents_after_two_day_grace_period():
    application = FeeApplication(
        LoanRepository(Loan('L1', date(2026, 1, 16))),
        FixedClock(),
    )

    fee = application.calculate('L1')

    assert fee.days_late == 3
    assert fee.amount_cents == 75


@pytest.mark.parametrize(
    ('days_late', 'amount_cents'),
    [(-2, 0), (0, 0), (1, 0), (2, 0), (3, 75), (50, 1000)],
)
def test_fee_calculation_applies_grace_period_and_cap(days_late, amount_cents):
    due_on = date(2026, 1, 19)
    loan = Loan('L1', due_on - date.resolution * days_late)
    application = FeeApplication(LoanRepository(loan), FixedClock())

    fee = application.calculate('L1')

    assert fee.days_late == max(0, days_late)
    assert fee.amount_cents == amount_cents


def test_fee_calculation_uses_the_return_date_when_loan_is_returned():
    loan = Loan('L1', date(2026, 1, 16), date(2026, 1, 18))
    application = FeeApplication(LoanRepository(loan), FixedClock())

    fee = application.calculate('L1')

    assert fee.days_late == 2
    assert fee.amount_cents == 0


def test_fee_calculation_returns_none_for_an_unknown_loan():
    application = FeeApplication(LoanRepository(), FixedClock())

    assert application.calculate('missing') is None


def test_payment_use_case_charges_a_known_loan():
    response = PaymentResponse(200, 'charged\n')
    gateway = RecordingGateway(response)
    application = PaymentApplication(LoanRepository(Loan('L1', date(2026, 1, 16))), gateway)

    result = application.pay('L1')

    assert result == response
    assert gateway.calls == ['L1']


def test_payment_use_case_rejects_an_unknown_loan_without_calling_gateway():
    gateway = RecordingGateway(PaymentResponse(200, 'charged\n'))
    application = PaymentApplication(LoanRepository(), gateway)

    result = application.pay('missing')

    assert result is None
    assert gateway.calls == []
