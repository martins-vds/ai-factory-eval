from datetime import date

from src.fees.gateway import HttpPaymentGateway
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


def test_network_failure_remains_available_with_gateway_failure():
    failure = OSError('connection failed')
    gateway = PaymentGateway(failure=failure)
    application = PaymentApplication(LoanRepository(Loan('L1')), gateway)

    result = application.pay('L1')

    assert result.status_code == 502
    assert result.body == 'payment gateway unavailable\n'
    assert result.failure is failure


def test_gateway_uses_the_characterized_default_url(monkeypatch):
    class GatewayReply:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return None

        def read(self):
            return b'charged\n'

    requests = []

    def open_request(request):
        requests.append(request.full_url)
        return GatewayReply()

    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    monkeypatch.setattr('src.fees.gateway.urlopen', open_request)

    response = HttpPaymentGateway().charge('L1')

    assert response == GatewayResponse(200, 'charged\n')
    assert requests == [
        'https://payments.lending-library.invalid/charge?loan=L1',
    ]
