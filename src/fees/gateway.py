import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen


DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class PaymentGatewayError(Exception):
    pass


def charge_loan(loan_id):
    gateway = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
    request = Request(f'{gateway}/charge?loan={loan_id}', method='POST')
    try:
        with urlopen(request) as response:
            return response.status, response.read().decode('utf-8')
    except HTTPError as response:
        return response.code, response.read().decode('utf-8')
    except OSError as error:
        raise PaymentGatewayError('payment gateway unavailable') from error
