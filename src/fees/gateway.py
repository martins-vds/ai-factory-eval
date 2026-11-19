import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .services import GatewayResponse, PaymentGatewayError

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class HttpPaymentGateway:
    def __init__(self, base_url=None):
        self.base_url = (
            base_url
            if base_url is not None
            else os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
        )

    def charge(self, loan_id):
        query = urlencode({'loan': loan_id})
        request = Request(f'{self.base_url.rstrip("/")}/charge?{query}', method='POST')
        try:
            with urlopen(request) as response:
                return GatewayResponse(response.status, response.read().decode())
        except HTTPError as error:
            return GatewayResponse(error.code, error.read().decode())
        except (URLError, OSError) as error:
            raise PaymentGatewayError('payment gateway unavailable') from error
