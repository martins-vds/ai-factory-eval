import os
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .services import (
    GatewayResponse,
    PaymentGatewayInterrupted,
    PaymentGatewayUnavailable,
)

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


urlopen = build_opener(NoRedirectHandler()).open


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
        request = Request(f'{gateway_url}/charge?loan={loan_id}', method='POST')
        try:
            with urlopen(request) as response:
                return GatewayResponse(
                    response.status,
                    response.read().decode('utf-8', errors='replace'),
                )
        except HTTPError as error:
            return GatewayResponse(
                error.code,
                error.read().decode('utf-8', errors='replace'),
            )
        except InterruptedError as error:
            raise PaymentGatewayInterrupted('payment gateway interrupted') from error
        except URLError as error:
            if isinstance(error.reason, InterruptedError):
                raise PaymentGatewayInterrupted('payment gateway interrupted') from error.reason
            raise PaymentGatewayUnavailable('payment gateway unavailable') from error
        except OSError as error:
            raise PaymentGatewayUnavailable('payment gateway unavailable') from error
