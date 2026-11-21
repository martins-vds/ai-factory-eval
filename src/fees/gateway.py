import os
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .services import GatewayResponse, PaymentGatewayFailure


DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
        request = Request(f'{gateway_url}/charge?loan={loan_id}', method='POST')
        try:
            with urlopen(request) as response:
                return GatewayResponse(response.status, response.read().decode())
        except HTTPError as error:
            return GatewayResponse(error.code, error.read().decode())
        except InterruptedError as error:
            raise PaymentGatewayFailure('payment gateway unavailable') from error
        except (HTTPException, OSError, TimeoutError, URLError) as error:
            raise PaymentGatewayFailure('payment gateway unavailable') from error
