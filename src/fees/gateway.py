import os
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .services import PaymentGatewayError, PaymentGatewayResponse

DEFAULT_PAYMENT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        return None


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
            with build_opener(NoRedirectHandler()).open(request) as response:
                body = response.read().decode(errors='replace')
                return PaymentGatewayResponse(response.status, body)
        except HTTPError as error:
            try:
                body = error.read().decode(errors='replace')
            finally:
                error.close()
            return PaymentGatewayResponse(error.code, body)
        except (HTTPException, OSError, URLError) as error:
            raise PaymentGatewayError('payment gateway unavailable') from error
