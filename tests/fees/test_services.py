from dataclasses import dataclass
from datetime import date

import pytest

from src.fees.services import FeeApplication, PaymentApplication, PaymentGatewayUnavailable


@dataclass
class Loan:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if loan_id == self.loan.id else None


class Clock:
    def today(self):
        return date(2026, 11, 10)


@dataclass
class GatewayResponse:
    status_code: int
    body: str


class PaymentGateway:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def charge(self, loan_id):
        self.calls.append(loan_id)
        if self.error:
            raise self.error
        return self.response


def test_fee_starts_at_twenty_five_cents_per_day_after_grace_period():
    loan = Loan(id='L1', due_on=date(2026, 11, 7))
    application = FeeApplication(LoanRepository(loan), Clock())

    fee = application.calculate('L1')

    assert fee.loan_id == 'L1'
    assert fee.due_on == date(2026, 11, 7)
    assert fee.days_late == 3
    assert fee.amount_cents == 75


def test_fee_is_waived_through_two_days_and_capped_at_ten_dollars():
    repository = LoanRepository(Loan(id='L1', due_on=date(2026, 11, 8)))
    application = FeeApplication(repository, Clock())

    two_days_late = application.calculate('L1')
    repository.loan = Loan(id='L1', due_on=date(2026, 11, 7))
    three_days_late = application.calculate('L1')
    repository.loan = Loan(id='L1', due_on=date(2026, 9, 1))
    capped = application.calculate('L1')

    assert two_days_late.days_late == 2
    assert two_days_late.amount_cents == 0
    assert three_days_late.amount_cents == 75
    assert capped.amount_cents == 1000


def test_fee_uses_return_date_and_never_charges_for_early_returns():
    returned_loan = Loan(
        id='L1',
        due_on=date(2026, 11, 7),
        returned_on=date(2026, 11, 8),
    )
    application = FeeApplication(LoanRepository(returned_loan), Clock())

    returned_fee = application.calculate('L1')

    assert returned_fee.days_late == 1
    assert returned_fee.amount_cents == 0

    early_loan = Loan(id='L2', due_on=date(2026, 11, 11))
    application = FeeApplication(LoanRepository(early_loan), Clock())

    early_fee = application.calculate('L2')

    assert early_fee.days_late == 0
    assert early_fee.amount_cents == 0


def test_fee_application_returns_none_for_an_unknown_loan():
    application = FeeApplication(LoanRepository(Loan(id='L1', due_on=date(2026, 11, 7))), Clock())

    assert application.calculate('unknown') is None


def test_payment_checks_for_a_loan_before_calling_the_gateway():
    gateway = PaymentGateway()
    application = PaymentApplication(
        LoanRepository(Loan(id='L1', due_on=date(2026, 11, 7))),
        gateway,
    )

    result = application.pay('unknown')

    assert result.status_code == 404
    assert result.body == 'no such loan\n'
    assert gateway.calls == []


def test_payment_forwards_success_and_maps_other_gateway_status_to_bad_gateway():
    repository = LoanRepository(Loan(id='L1', due_on=date(2026, 11, 7)))
    successful_gateway = PaymentGateway(response=GatewayResponse(200, 'charged\n'))
    failed_gateway = PaymentGateway(response=GatewayResponse(503, 'declined\n'))

    success = PaymentApplication(repository, successful_gateway).pay('L1')
    failure = PaymentApplication(repository, failed_gateway).pay('L1')

    assert (success.status_code, success.body) == (200, 'charged\n')
    assert (failure.status_code, failure.body) == (502, 'declined\n')


def test_payment_failure_keeps_an_interruption_as_the_gateway_failure_cause():
    interruption = InterruptedError('request interrupted')
    gateway = PaymentGateway(error=interruption)
    application = PaymentApplication(
        LoanRepository(Loan(id='L1', due_on=date(2026, 11, 7))),
        gateway,
    )

    with pytest.raises(PaymentGatewayUnavailable) as failure:
        application.pay('L1')

    assert failure.value.__cause__ is interruption


def test_payment_failure_keeps_an_io_error_as_the_gateway_failure_cause():
    io_error = OSError('connection failed')
    gateway = PaymentGateway(error=io_error)
    application = PaymentApplication(
        LoanRepository(Loan(id='L1', due_on=date(2026, 11, 7))),
        gateway,
    )

    with pytest.raises(PaymentGatewayUnavailable) as failure:
        application.pay('L1')

    assert failure.value.__cause__ is io_error
