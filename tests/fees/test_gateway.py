import pytest

from src.fees.gateway import HttpPaymentGateway
from src.fees.services import PaymentGatewayFailure


class GatewayResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return b'charged\n'


def test_gateway_uses_the_source_default_and_sends_a_bodyless_post(monkeypatch):
    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    requests = []
    monkeypatch.setattr(
        'src.fees.gateway.urlopen',
        lambda request: requests.append(request) or GatewayResponse(),
    )

    response = HttpPaymentGateway().charge('L1')

    assert response.status_code == 200
    assert response.body == 'charged\n'
    assert requests[0].full_url == ('https://payments.lending-library.invalid/charge?loan=L1')
    assert requests[0].get_method() == 'POST'
    assert requests[0].data is None


def test_gateway_prefers_explicit_base_url_over_environment(monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'http://environment.invalid')
    requests = []
    monkeypatch.setattr(
        'src.fees.gateway.urlopen',
        lambda request: requests.append(request) or GatewayResponse(),
    )

    HttpPaymentGateway('http://configured.invalid').charge('L1')

    assert requests[0].full_url == 'http://configured.invalid/charge?loan=L1'


def test_gateway_keeps_an_interruption_as_the_failure_cause(monkeypatch):
    interruption = InterruptedError('request interrupted')

    def interrupt(_request):
        raise interruption

    monkeypatch.setattr('src.fees.gateway.urlopen', interrupt)

    with pytest.raises(PaymentGatewayFailure) as failure:
        HttpPaymentGateway('http://gateway.invalid').charge('L1')

    assert str(failure.value) == 'payment gateway unavailable'
    assert failure.value.__cause__ is interruption
