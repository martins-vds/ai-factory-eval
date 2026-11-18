from urllib.error import URLError

import pytest

from src.fees.gateway import HttpPaymentGateway


def test_http_payment_gateway_sends_empty_post_to_charge_endpoint(payment_gateway_server):
    received, _, _ = payment_gateway_server
    response = HttpPaymentGateway().charge('L1')

    assert received == [('POST', '/charge?loan=L1', b'')]
    assert (response.status_code, response.body) == (200, 'charged\n')


def test_http_payment_gateway_preserves_non_success_status_and_body(payment_gateway_server):
    received, configured_response, _ = payment_gateway_server
    configured_response.update(status=503, body=b'declined\n')

    response = HttpPaymentGateway().charge('L1')

    assert received == [('POST', '/charge?loan=L1', b'')]
    assert (response.status_code, response.body) == (503, 'declined\n')


def test_http_payment_gateway_does_not_follow_redirects(payment_gateway_server):
    received, configured_response, _ = payment_gateway_server
    configured_response.update(
        status=302,
        body=b'moved\n',
        headers={'Location': '/redirected'},
    )

    response = HttpPaymentGateway().charge('L1')

    assert received == [('POST', '/charge?loan=L1', b'')]
    assert (response.status_code, response.body) == (302, 'moved\n')


def test_http_payment_gateway_uses_the_characterized_default_url(monkeypatch):
    class Opener:
        def open(self, request):
            assert request.full_url == ('https://payments.lending-library.invalid/charge?loan=L1')
            raise URLError('unavailable')

    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    monkeypatch.setattr('src.fees.gateway.build_opener', lambda *handlers: Opener())

    with pytest.raises(URLError):
        HttpPaymentGateway().charge('L1')


def test_http_payment_gateway_does_not_discard_an_interruption(monkeypatch):
    interruption = InterruptedError('request interrupted')

    def interrupt(request):
        raise URLError(interruption)

    class Opener:
        def open(self, request):
            return interrupt(request)

    monkeypatch.setattr('src.fees.gateway.build_opener', lambda *handlers: Opener())

    with pytest.raises(InterruptedError) as caught:
        HttpPaymentGateway().charge('L1')

    assert caught.value is interruption
