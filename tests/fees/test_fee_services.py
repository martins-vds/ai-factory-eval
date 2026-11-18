from dataclasses import FrozenInstanceError, dataclass
from datetime import date
from decimal import Decimal

import pytest

from src.fees.services import Fee, FeeApplication, PaymentResult


@dataclass
class Loan:
    id: str
    due_on: date
    member: str = 'reader'
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if loan_id == self.loan.id else None


class Clock:
    def today(self):
        return date(2026, 11, 18)


class PaymentGateway:
    def charge(self, loan_id):
        raise AssertionError('fee calculation must not charge a payment')


class RecordingPaymentGateway:
    def __init__(self, result):
        self.result = result
        self.charged_loan_ids = []

    def charge(self, loan_id):
        self.charged_loan_ids.append(loan_id)
        return self.result


def test_fee_calculation_waives_the_first_two_days_and_charges_the_third():
    loan = Loan(id='L1', due_on=date(2026, 11, 16))
    application = FeeApplication(LoanRepository(loan), Clock(), PaymentGateway())

    two_days_late = application.calculate(loan.id)
    loan.due_on = date(2026, 11, 15)
    three_days_late = application.calculate(loan.id)

    assert (two_days_late.days_late, two_days_late.amount) == (2, Decimal('0.00'))
    assert (three_days_late.days_late, three_days_late.amount) == (3, Decimal('0.75'))


def test_fee_calculation_uses_return_date_and_never_exceeds_ten_dollars():
    loan = Loan(
        id='L1',
        due_on=date(2026, 1, 1),
        returned_on=date(2026, 3, 1),
    )
    application = FeeApplication(LoanRepository(loan), Clock(), PaymentGateway())

    fee = application.calculate(loan.id)

    assert fee.days_late == 59
    assert fee.amount == Decimal('10.00')


def test_fee_calculation_clamps_days_before_the_due_date_to_zero():
    loan = Loan(id='L1', due_on=date(2026, 11, 19))
    application = FeeApplication(LoanRepository(loan), Clock(), PaymentGateway())

    fee = application.calculate(loan.id)

    assert fee.days_late == 0
    assert fee.amount == Decimal('0.00')


def test_fee_application_returns_none_for_an_unknown_loan():
    loan = Loan(id='L1', due_on=date(2026, 11, 18))
    application = FeeApplication(LoanRepository(loan), Clock(), PaymentGateway())

    assert application.calculate('missing') is None


def test_fee_application_does_not_charge_for_an_unknown_loan():
    loan = Loan(id='L1', due_on=date(2026, 11, 18))
    gateway = RecordingPaymentGateway(PaymentResult(200, 'charged\n'))
    application = FeeApplication(LoanRepository(loan), Clock(), gateway)

    assert application.pay('missing') is None
    assert gateway.charged_loan_ids == []


def test_fee_application_returns_the_gateway_result_for_an_existing_loan():
    loan = Loan(id='L1', due_on=date(2026, 11, 18))
    result = PaymentResult(502, 'declined\n')
    gateway = RecordingPaymentGateway(result)
    application = FeeApplication(LoanRepository(loan), Clock(), gateway)

    assert application.pay(loan.id) == result
    assert gateway.charged_loan_ids == [loan.id]


def test_fee_and_payment_results_are_immutable():
    fee = Fee(
        loan=Loan('L1', date(2026, 11, 18)),
        days_late=0,
        amount=Decimal('0.00'),
    )
    payment = PaymentResult(status=200, body='charged\n')

    with pytest.raises(FrozenInstanceError):
        fee.days_late = 1
    with pytest.raises(FrozenInstanceError):
        payment.status = 502
