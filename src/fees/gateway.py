import os
from dataclasses import dataclass
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
import urllib.request


DEFAULT_PAYMENT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class PaymentGatewayUnavailable(Exception):
    pass


class PaymentGatewayInterrupted(PaymentGatewayUnavailable):
    pass


@dataclass(frozen=True)
class PaymentResult:
    status_code: int
    body: bytes


def charge_loan(loan_id):
    gateway_url = os.environ.get(
        'PAYMENT_GATEWAY_URL',
        DEFAULT_PAYMENT_GATEWAY_URL,
    )
    query = urlencode({'loan': loan_id})
    request = urllib.request.Request(
        f'{gateway_url}/charge?{query}',
        data=b'',
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            status_code = 200 if response.status == 200 else 502
            return PaymentResult(status_code, response.read())
    except HTTPError as error:
        return PaymentResult(502, error.read())
    except InterruptedError as error:
        raise PaymentGatewayInterrupted from error
    except (HTTPException, OSError, URLError) as error:
        raise PaymentGatewayUnavailable from error
