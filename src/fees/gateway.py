import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .services import GatewayResponse, PaymentGatewayError

DEFAULT_PAYMENT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_PAYMENT_GATEWAY_URL).rstrip('/')
        url = f'{gateway_url}/charge?{urlencode({"loan": loan_id})}'
        request = Request(url, data=b'', method='POST')

        try:
            with build_opener(_NoRedirectHandler()).open(request, timeout=5) as response:
                return GatewayResponse(response.status, self._decode(response.read()))
        except HTTPError as response:
            return GatewayResponse(response.code, self._decode(response.read()))
        except InterruptedError:
            raise
        except (URLError, OSError) as error:
            raise PaymentGatewayError('Payment gateway is unavailable') from error

    @staticmethod
    def _decode(body: bytes) -> str:
        return body.decode('utf-8', errors='replace')
