import os
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .services import GatewayResponse

DEFAULT_PAYMENT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_PAYMENT_GATEWAY_URL).rstrip('/')
        url = f'{gateway_url}/charge?{urlencode({"loan": loan_id})}'
        request = Request(url, method='POST')

        try:
            with urlopen(request) as response:
                return GatewayResponse(response.status, response.read().decode('utf-8'))
        except HTTPError as error:
            try:
                return GatewayResponse(error.code, error.read().decode('utf-8'))
            finally:
                error.close()
