import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .services import GatewayResponse, PaymentGatewayFailure


class HttpPaymentGateway:
    def __init__(self, base_url=None):
        self.base_url = base_url

    def charge(self, loan_id):
        base_url = self.base_url
        if base_url is None:
            base_url = os.environ.get(
                'PAYMENT_GATEWAY_URL',
                'https://payments.lending-library.invalid',
            )
        request = Request(f'{base_url}/charge?loan={loan_id}', method='POST')

        try:
            response = urlopen(request)
        except HTTPError as error:
            response = error
        except (URLError, OSError) as error:
            cause = error.reason if isinstance(error, URLError) else error
            raise PaymentGatewayFailure('payment gateway unavailable') from cause

        with response:
            return GatewayResponse(
                response.status,
                response.read().decode('utf-8'),
            )
