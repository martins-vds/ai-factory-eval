import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class GatewayUnavailable(Exception):
    pass


@dataclass(frozen=True)
class GatewayResponse:
    status_code: int
    body: str


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        return None


def open_gateway_request(request):
    return build_opener(NoRedirectHandler).open(request)


class HttpPaymentGateway:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url

    def charge(self, loan_id: str) -> GatewayResponse:
        base_url = self.base_url
        if base_url is None:
            base_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
        request = Request(
            f'{base_url.rstrip("/")}/charge?{urlencode({"loan": loan_id})}',
            method='POST',
        )
        try:
            with open_gateway_request(request) as response:
                return GatewayResponse(
                    status_code=response.status,
                    body=response.read().decode('utf-8', errors='replace'),
                )
        except HTTPError as response:
            return GatewayResponse(
                status_code=response.code,
                body=response.read().decode('utf-8', errors='replace'),
            )
        except InterruptedError as error:
            raise GatewayUnavailable('payment gateway unavailable') from error
        except (URLError, OSError) as error:
            raise GatewayUnavailable('payment gateway unavailable') from error
