from datetime import date

from src.fees.services import GatewayResponse, PaymentApplication


class Loan:
    def __init__(self, loan_id):
        self.id = loan_id
        self.due_on = date(2026, 11, 22)
        self.returned_on = None


class LoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan and self.loan.id == loan_id else None


class PaymentGateway:
    def __init__(self, response=None, failure=None):
        self.calls = []
        self.response = response
        self.failure = failure

    def charge(self, loan_id):
        self.calls.append(loan_id)
        if self.failure:
            raise self.failure
        return self.response


def test_missing_loan_is_not_sent_to_the_payment_gateway():
    gateway = PaymentGateway()
    application = PaymentApplication(
        LoanRepository(Loan('L1')),
        gateway,
    )

    result = application.pay('missing')

    assert result is None
    assert gateway.calls == []


def test_payment_success_preserves_the_gateway_body():
    gateway = PaymentGateway(GatewayResponse(200, 'charged\n'))
    application = PaymentApplication(LoanRepository(Loan('L1')), gateway)

    result = application.pay('L1')

    assert result.status_code == 200
    assert result.body == 'charged\n'
    assert result.failure is None
    assert gateway.calls == ['L1']


def test_non_success_gateway_status_becomes_bad_gateway_with_its_body():
    gateway = PaymentGateway(GatewayResponse(503, 'declined\n'))
    application = PaymentApplication(LoanRepository(Loan('L1')), gateway)

    result = application.pay('L1')

    assert result.status_code == 502
    assert result.body == 'declined\n'


def test_interrupted_payment_remains_available_with_gateway_failure():
    interruption = InterruptedError('request interrupted')
    gateway = PaymentGateway(failure=interruption)
    application = PaymentApplication(LoanRepository(Loan('L1')), gateway)

    result = application.pay('L1')

    assert result.status_code == 502
    assert result.body == 'payment gateway unavailable\n'
    assert result.failure is interruption
