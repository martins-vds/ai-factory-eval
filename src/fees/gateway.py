import os
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .services import GatewayResponse

DEFAULT_PAYMENT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


class HttpPaymentGateway:
    def __init__(self, base_url=None):
        self.base_url = base_url

    def charge(self, loan_id: str) -> GatewayResponse:
        base_url = self.base_url or os.environ.get(
            'PAYMENT_GATEWAY_URL', DEFAULT_PAYMENT_GATEWAY_URL
        )
        request = Request(f'{base_url}/charge?loan={loan_id}', method='POST')

        try:
            with build_opener(NoRedirectHandler()).open(request, timeout=5) as response:
                return GatewayResponse(response.status, response.read())
        except HTTPError as response:
            return GatewayResponse(response.code, response.read())
