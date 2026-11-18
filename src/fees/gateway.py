import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .services import GatewayResponse, PaymentGatewayError


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        return None


class HttpPaymentGateway:
    def __init__(self, base_url=None, opener=None):
        self.base_url = base_url
        self.opener = opener or build_opener(_NoRedirectHandler())

    def charge(self, loan_id):
        base_url = self.base_url or os.environ.get(
            'PAYMENT_GATEWAY_URL',
            'https://payments.lending-library.invalid',
        )
        url = f'{base_url.rstrip("/")}/charge?{urlencode({"loan": loan_id})}'
        outbound_request = Request(url, method='POST')

        try:
            with self.opener.open(outbound_request) as response:
                return GatewayResponse(
                    response.status,
                    response.read().decode('utf-8', errors='replace'),
                )
        except HTTPError as response:
            with response:
                return GatewayResponse(
                    response.code,
                    response.read().decode('utf-8', errors='replace'),
                )
        except (OSError, URLError) as exc:
            raise PaymentGatewayError('payment gateway unavailable') from exc
