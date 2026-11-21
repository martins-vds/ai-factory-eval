import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .services import GatewayResponse

DEFAULT_PAYMENT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        return None


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        base_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_PAYMENT_GATEWAY_URL).rstrip('/')
        url = f'{base_url}/charge?{urlencode({"loan": loan_id})}'
        request = Request(url, method='POST')

        try:
            with build_opener(NoRedirectHandler).open(request) as response:
                body = response.read().decode('utf-8', errors='replace')
                return GatewayResponse(response.status, body)
        except HTTPError as response:
            body = response.read().decode('utf-8', errors='replace')
            return GatewayResponse(response.code, body)
        except URLError as error:
            if isinstance(error.reason, InterruptedError):
                raise error.reason from error
            raise OSError(error.reason) from error
