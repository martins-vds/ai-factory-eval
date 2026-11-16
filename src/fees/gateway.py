import os
from http.client import HTTPException
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class PaymentGatewayFailure(Exception):
    pass


def charge_loan(loan_id):
    gateway_url = os.environ.get(
        'PAYMENT_GATEWAY_URL',
        'https://payments.lending-library.invalid',
    )
    url = f'{gateway_url.rstrip("/")}/charge?{urlencode({"loan": loan_id})}'
    request = Request(url, data=b'', method='POST')
    try:
        with urlopen(request) as response:
            return response.status, response.read()
    except HTTPError as response:
        with response:
            return response.code, response.read()
    except (HTTPException, OSError) as error:
        raise PaymentGatewayFailure('payment gateway unavailable\n') from error
