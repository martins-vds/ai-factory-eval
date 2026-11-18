import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .services import GatewayResponse, GatewayUnavailable

DEFAULT_GATEWAY_URL = 'http://localhost:9999'


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


class HttpPaymentGateway:
    def __init__(self, gateway_url=None):
        self.gateway_url = gateway_url

    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = self.gateway_url or os.environ.get(
            'PAYMENT_GATEWAY_URL',
            DEFAULT_GATEWAY_URL,
        )
        parsed_url = urlsplit(gateway_url)
        if parsed_url.scheme not in {'http', 'https'} or not parsed_url.netloc:
            raise GatewayUnavailable
        request = Request(
            f'{gateway_url.rstrip("/")}/charge?loan={quote(loan_id, safe="")}',
            data=b'',
            method='POST',
        )
        opener = build_opener(NoRedirectHandler())
        try:
            with opener.open(request) as response:
                status = response.status
                body = response.read()
        except HTTPError as error:
            status = error.code
            try:
                body = error.read()
            except InterruptedError as read_error:
                raise GatewayUnavailable from read_error
            except (OSError, URLError) as read_error:
                raise GatewayUnavailable from read_error
        except InterruptedError as error:
            raise GatewayUnavailable from error
        except (OSError, URLError) as error:
            raise GatewayUnavailable from error

        return GatewayResponse(status=status, body=body)
