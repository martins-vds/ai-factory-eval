import pytest

from src.fees.gateway import GatewayFailure, HttpPaymentGateway


def test_http_payment_gateway_preserves_interruption_when_wrapping_failure(monkeypatch):
    interruption = InterruptedError('payment request interrupted')

    def interrupted(*args, **kwargs):
        raise interruption

    monkeypatch.setattr('src.fees.gateway.request.urlopen', interrupted)

    with pytest.raises(GatewayFailure) as failure:
        HttpPaymentGateway().charge('L1')

    assert str(failure.value) == ''
    assert failure.value.__cause__ is interruption


@pytest.mark.parametrize('wrapped', [False, True])
def test_http_payment_gateway_retains_interrupted_url_error(monkeypatch, wrapped):
    from urllib.error import URLError

    interruption = InterruptedError('payment request interrupted')
    failure = URLError(interruption) if wrapped else interruption

    def interrupted(*args, **kwargs):
        raise failure

    monkeypatch.setattr('src.fees.gateway.request.urlopen', interrupted)

    with pytest.raises(GatewayFailure) as gateway_failure:
        HttpPaymentGateway().charge('L1')

    assert gateway_failure.value.__cause__ is interruption


def test_http_payment_gateway_uses_the_configured_default_and_encodes_loan_id(monkeypatch):
    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'charged\n'

    requests = []

    def open_request(outbound_request):
        requests.append(outbound_request.full_url)
        return Response()

    monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    monkeypatch.setattr('src.fees.gateway.request.urlopen', open_request)

    result = HttpPaymentGateway().charge('L/1')

    assert result.status_code == 200
    assert requests == ['https://payments.lending-library.invalid/charge?loan=L%2F1']
