from dataclasses import dataclass
from datetime import date

from src.fees.services import FeeApplication, GatewayResponse, PaymentApplication


@dataclass
class Loan:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan and self.loan.id == loan_id else None


class FixedClock:
    def today(self):
        return date(2026, 11, 22)


class PaymentGateway:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.charged = []

    def charge(self, loan_id):
        self.charged.append(loan_id)
        if self.error:
            raise self.error
        return self.response


def fee_for(*, due_on, returned_on=None):
    loan = Loan('L1', due_on, returned_on)
    return FeeApplication(LoanRepository(loan), FixedClock()).calculate_fee('L1')


def test_fee_is_waived_through_two_days_late():
    fee = fee_for(due_on=date(2026, 11, 20))

    assert (fee.late_days, fee.amount_cents) == (2, 0)


def test_fee_is_twenty_five_cents_per_day_after_grace_period():
    fee = fee_for(due_on=date(2026, 11, 19))

    assert (fee.late_days, fee.amount_cents) == (3, 75)


def test_fee_is_capped_at_ten_dollars():
    fee = fee_for(due_on=date(2026, 9, 1))

    assert fee.amount_cents == 1000


def test_early_or_on_time_loan_has_no_late_days():
    fee = fee_for(due_on=date(2026, 11, 23))

    assert (fee.late_days, fee.amount_cents) == (0, 0)


def test_return_date_is_used_instead_of_today_for_fee_calculation():
    fee = fee_for(due_on=date(2026, 11, 19), returned_on=date(2026, 11, 20))

    assert (fee.late_days, fee.amount_cents) == (1, 0)


def test_missing_loan_has_no_fee():
    fee = FeeApplication(LoanRepository(None), FixedClock()).calculate_fee('missing')

    assert fee is None


def test_missing_loan_is_rejected_before_payment_gateway_is_called():
    gateway = PaymentGateway(GatewayResponse(200, 'charged\n'))
    application = PaymentApplication(LoanRepository(None), gateway)

    result = application.pay('missing')

    assert result is None
    assert gateway.charged == []


def test_interrupted_payment_preserves_interrupt_while_reporting_gateway_failure():
    interruption = InterruptedError('request cancelled')
    gateway = PaymentGateway(error=interruption)
    application = PaymentApplication(LoanRepository(Loan('L1', date(2026, 11, 22))), gateway)

    result = application.pay('L1')

    assert (result.status_code, result.body) == (502, 'payment gateway unavailable\n')
    assert result.interruption is interruption


def test_payment_application_returns_success_only_for_gateway_http_200():
    gateway = PaymentGateway(GatewayResponse(200, 'charged\n'))
    application = PaymentApplication(
        LoanRepository(Loan('L1', date(2026, 11, 22))),
        gateway,
    )

    result = application.pay('L1')

    assert (result.status_code, result.body) == (200, 'charged\n')


def test_payment_application_maps_non_200_response_to_bad_gateway():
    gateway = PaymentGateway(GatewayResponse(503, 'declined\n'))
    application = PaymentApplication(
        LoanRepository(Loan('L1', date(2026, 11, 22))),
        gateway,
    )

    result = application.pay('L1')

    assert (result.status_code, result.body) == (502, 'declined\n')


def test_payment_application_maps_io_failure_to_gateway_unavailable():
    gateway = PaymentGateway(error=OSError('connection refused'))
    application = PaymentApplication(
        LoanRepository(Loan('L1', date(2026, 11, 22))),
        gateway,
    )

    result = application.pay('L1')

    assert (result.status_code, result.body) == (
        502,
        'payment gateway unavailable\n',
    )
