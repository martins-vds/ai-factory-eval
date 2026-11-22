import http.client
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .services import PaymentGatewayFailure, PaymentResult


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


class HttpPaymentGateway:
    def __init__(self, base_url=None):
        self.base_url = base_url

    def charge(self, loan_id):
        base_url = self.base_url
        if base_url is None:
            base_url = os.environ.get(
                'PAYMENT_GATEWAY_URL',
                'https://payments.lending-library.invalid',
            )
        url = f'{base_url}/charge?{urlencode({"loan": loan_id})}'
        request = Request(url, method='POST')
        opener = build_opener(NoRedirectHandler())

        try:
            with opener.open(request) as response:
                return PaymentResult(response.status, response.read().decode('utf-8'))
        except HTTPError as response:
            try:
                body = response.read().decode('utf-8')
            finally:
                response.close()
            return PaymentResult(response.code, body)
        except InterruptedError as error:
            raise PaymentGatewayFailure() from error
        except (OSError, URLError, http.client.HTTPException) as error:
            raise PaymentGatewayFailure() from error
