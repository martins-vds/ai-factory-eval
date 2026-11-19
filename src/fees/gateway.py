import os
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .services import PaymentGatewayError, PaymentGatewayResponse

DEFAULT_PAYMENT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class HttpPaymentGateway:
    def __init__(self, base_url: str | None = None):
        self.base_url = (
            base_url
            if base_url is not None
            else os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_PAYMENT_GATEWAY_URL)
        )

    def charge(self, loan_id: str) -> PaymentGatewayResponse:
        request = Request(f'{self.base_url}/charge?loan={loan_id}', method='POST')
        try:
            with urlopen(request) as response:
                body = response.read().decode(errors='replace')
                return PaymentGatewayResponse(response.status, body)
        except HTTPError as error:
            body = error.read().decode(errors='replace')
            return PaymentGatewayResponse(error.code, body)
        except (HTTPException, OSError, URLError) as error:
            raise PaymentGatewayError('payment gateway unavailable') from error
