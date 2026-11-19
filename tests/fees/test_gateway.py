import pytest

from src.fees import gateway
from src.fees.gateway import HttpPaymentGateway
from src.fees.services import PaymentGatewayError


def test_payment_gateway_sends_post_without_body_and_returns_gateway_response(local_gateway):
    base_url, requests = local_gateway
    gateway = HttpPaymentGateway(base_url)

    response = gateway.charge('L1')

    assert (response.status_code, response.body) == (200, 'charged\n')
    assert requests == [('POST', '/charge?loan=L1', b'')]


def test_payment_gateway_returns_non_success_body_for_application_mapping(local_gateway):
    base_url, requests = local_gateway
    gateway = HttpPaymentGateway(base_url)

    response = gateway.charge('L2')

    assert (response.status_code, response.body) == (503, 'declined\n')
    assert requests == [('POST', '/charge?loan=L2', b'')]


def test_payment_gateway_does_not_follow_redirects(local_gateway):
    base_url, requests = local_gateway
    gateway = HttpPaymentGateway(base_url)

    response = gateway.charge('L3')

    assert (response.status_code, response.body) == (302, '')
    assert requests == [('POST', '/charge?loan=L3', b'')]


def test_payment_gateway_keeps_interrupted_failure_as_exception_cause(monkeypatch):
    interruption = InterruptedError('request interrupted')

    class InterruptedOpener:
        def open(self, request):
            raise interruption

    monkeypatch.setattr(gateway, 'build_opener', lambda *handlers: InterruptedOpener())

    with pytest.raises(PaymentGatewayError) as raised:
        HttpPaymentGateway('http://payments.example').charge('L1')

    assert raised.value.__cause__ is interruption


def test_payment_gateway_uses_configured_or_source_default_url(monkeypatch):
    monkeypatch.setenv('PAYMENT_GATEWAY_URL', 'https://gateway.example')
    assert HttpPaymentGateway().base_url == 'https://gateway.example'

    monkeypatch.delenv('PAYMENT_GATEWAY_URL')
    assert HttpPaymentGateway().base_url == 'https://payments.lending-library.invalid'
