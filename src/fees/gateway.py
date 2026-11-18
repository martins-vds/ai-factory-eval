import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener


@dataclass(frozen=True)
class PaymentGatewayResponse:
    status_code: int
    body: str


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> PaymentGatewayResponse:
        gateway_url = os.environ.get(
            'PAYMENT_GATEWAY_URL',
            'https://payments.lending-library.invalid',
        )
        url = f'{gateway_url}/charge?{urlencode({"loan": loan_id})}'
        request = Request(url, method='POST')

        try:
            with build_opener(_NoRedirectHandler()).open(request) as response:
                status_code = response.status
                body = response.read().decode('utf-8', errors='replace')
        except HTTPError as error:
            with error:
                status_code = error.code
                body = error.read().decode('utf-8', errors='replace')
        except URLError as error:
            if isinstance(error.reason, InterruptedError):
                raise error.reason
            raise

        return PaymentGatewayResponse(status_code, body)
