import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class GatewayUnavailable(Exception):
    pass


@dataclass(frozen=True)
class PaymentResponse:
    status: int
    body: str


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, new_url):
        return None


class PaymentGateway:
    def __init__(self, base_url=None):
        self.base_url = base_url

    def charge(self, loan_id):
        base_url = (
            self.base_url
            if self.base_url is not None
            else os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
        )
        request = Request(
            f'{base_url}/charge?{urlencode({"loan": loan_id})}',
            method='POST',
        )
        try:
            with build_opener(_NoRedirectHandler()).open(request) as response:
                status = response.status
                body = response.read().decode('utf-8', errors='replace')
        except HTTPError as response:
            body = response.read().decode('utf-8', errors='replace')
            return PaymentResponse(502, body)
        except InterruptedError as error:
            raise GatewayUnavailable('payment gateway unavailable') from error
        except (OSError, URLError) as error:
            raise GatewayUnavailable('payment gateway unavailable') from error

        return PaymentResponse(200 if status == 200 else 502, body)
