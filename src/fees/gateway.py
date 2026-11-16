import os
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener


DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class PaymentGatewayError(Exception):
    pass


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        return None


def charge_loan(loan_id):
    gateway = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
    request = Request(f'{gateway}/charge?loan={loan_id}', method='POST')
    try:
        with build_opener(_NoRedirectHandler).open(request) as response:
            return response.status, response.read().decode('utf-8', errors='replace')
    except HTTPError as response:
        with response:
            return response.code, response.read().decode('utf-8', errors='replace')
    except OSError as error:
        raise PaymentGatewayError('payment gateway unavailable') from error
