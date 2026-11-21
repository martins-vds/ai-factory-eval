import os
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .services import GatewayResponse, PaymentGatewayFailure

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


def _read_gateway_response(response, status_code):
    try:
        body = response.read().decode('utf-8', errors='replace')
    except InterruptedError as error:
        raise PaymentGatewayFailure from error
    except (HTTPException, OSError, TimeoutError, URLError) as error:
        raise PaymentGatewayFailure from error
    return GatewayResponse(status_code, body)


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
        request = Request(f'{gateway_url}/charge?loan={loan_id}', method='POST')
        try:
            with urlopen(request) as response:
                return _read_gateway_response(response, response.status)
        except HTTPError as error:
            return _read_gateway_response(error, error.code)
        except InterruptedError as error:
            raise PaymentGatewayFailure from error
        except (HTTPException, OSError, TimeoutError, URLError) as error:
            raise PaymentGatewayFailure from error
