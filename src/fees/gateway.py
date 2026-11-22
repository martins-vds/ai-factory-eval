import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .services import GatewayResponse, GatewayUnavailable

DEFAULT_PAYMENT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_PAYMENT_GATEWAY_URL)
        request = Request(f'{gateway_url}/charge?loan={loan_id}', method='POST')

        try:
            with urlopen(request) as response:
                return GatewayResponse(response.status, response.read())
        except HTTPError as response:
            return GatewayResponse(response.code, response.read())
        except (OSError, URLError) as error:
            raise GatewayUnavailable('payment gateway unavailable') from error
