import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


@dataclass
class GatewayResponse:
    status_code: int
    body: bytes


class PaymentGatewayFailure(Exception):
    pass


class PaymentGatewayInterrupted(PaymentGatewayFailure):
    pass


def charge_loan(loan_id: str) -> GatewayResponse:
    gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
    path = urlencode({'loan': loan_id})
    request = Request(f'{gateway_url}/charge?{path}', data=b'', method='POST')

    try:
        with urlopen(request) as response:
            status_code = response.status
            body = response.read()
    except HTTPError as response:
        return GatewayResponse(502, response.read())
    except InterruptedError as error:
        raise PaymentGatewayInterrupted from error
    except URLError as error:
        if isinstance(error.reason, InterruptedError):
            raise PaymentGatewayInterrupted from error.reason
        raise PaymentGatewayFailure from error
    except OSError as error:
        raise PaymentGatewayFailure from error

    return GatewayResponse(200 if status_code == 200 else 502, body)
