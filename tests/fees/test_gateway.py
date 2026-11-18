from io import BytesIO
from urllib.error import HTTPError, URLError

import pytest

from src.fees.gateway import HttpPaymentGateway, PaymentInterrupted
from src.fees.services import PaymentResult


class GatewayResponse:
    def __init__(self, status=200):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return b'charged\n'


@pytest.mark.parametrize(
    ('gateway_url', 'loan_id', 'expected_url'),
    [
        (
            None,
            'L1',
            'https://payments.lending-library.invalid/charge?loan=L1',
        ),
        ('https://gatewayX/', 'L 1/2', 'https://gatewayX/charge?loan=L+1%2F2'),
    ],
)
def test_payment_gateway_uses_source_default_or_configured_url(
    monkeypatch,
    gateway_url,
    loan_id,
    expected_url,
):
    requests = []

    def respond(request, *args, **kwargs):
        requests.append(request)
        return GatewayResponse()

    if gateway_url is None:
        monkeypatch.delenv('PAYMENT_GATEWAY_URL', raising=False)
    else:
        monkeypatch.setenv('PAYMENT_GATEWAY_URL', gateway_url)
    monkeypatch.setattr('src.fees.gateway.urlopen', respond)

    result = HttpPaymentGateway().charge(loan_id)

    assert result.body == 'charged\n'
    assert requests[0].full_url == expected_url
    assert requests[0].method == 'POST'
    assert requests[0].data == b''


def test_payment_gateway_maps_non_200_status_to_502(monkeypatch):
    monkeypatch.setattr(
        'src.fees.gateway.urlopen',
        lambda request: GatewayResponse(status=201),
    )

    result = HttpPaymentGateway().charge('L1')

    assert result == PaymentResult(502, 'charged\n')


def test_payment_gateway_maps_http_errors_to_502_and_preserves_body(monkeypatch):
    error = HTTPError(
        'https://gateway.invalid/charge?loan=L1',
        402,
        'Payment Required',
        None,
        BytesIO(b'declined\n'),
    )
    monkeypatch.setattr(
        'src.fees.gateway.urlopen',
        lambda request: (_ for _ in ()).throw(error),
    )

    result = HttpPaymentGateway().charge('L1')

    assert result == PaymentResult(502, 'declined\n')


@pytest.mark.parametrize(
    'error',
    [URLError('offline'), OSError('offline')],
)
def test_payment_gateway_maps_connection_errors_to_unavailable(monkeypatch, error):
    monkeypatch.setattr(
        'src.fees.gateway.urlopen',
        lambda request: (_ for _ in ()).throw(error),
    )

    result = HttpPaymentGateway().charge('L1')

    assert result == PaymentResult(502, 'payment gateway unavailable\n')


@pytest.mark.parametrize(
    'error',
    [
        URLError(InterruptedError('request cancelled')),
        InterruptedError('request cancelled'),
    ],
)
def test_payment_gateway_preserves_interruption_cause(monkeypatch, error):
    monkeypatch.setattr(
        'src.fees.gateway.urlopen',
        lambda request: (_ for _ in ()).throw(error),
    )

    with pytest.raises(PaymentInterrupted) as raised:
        HttpPaymentGateway().charge('L1')

    assert isinstance(raised.value.__cause__, InterruptedError)
