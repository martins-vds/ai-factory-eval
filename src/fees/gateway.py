import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class PaymentGatewayUnavailable(Exception):
    pass


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, url):
        return None


def open_url(request):
    return build_opener(_NoRedirectHandler).open(request)


def charge_loan(loan_id: str) -> tuple[int, bytes]:
    gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL).rstrip('/')
    url = f'{gateway_url}/charge?{urlencode({"loan": loan_id})}'
    request = Request(url, method='POST')

    try:
        with open_url(request) as response:
            return response.status, response.read()
    except HTTPError as response:
        return response.code, response.read()
    except InterruptedError as error:
        raise PaymentGatewayUnavailable from error
    except (OSError, URLError) as error:
        raise PaymentGatewayUnavailable from error
