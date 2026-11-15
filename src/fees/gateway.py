import os
from urllib import request as url_request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request

from .services import (
    GatewayResponse,
    PaymentGatewayInterrupted,
    PaymentGatewayUnavailable,
)

DEFAULT_PAYMENT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_PAYMENT_GATEWAY_URL)
        url = f'{gateway_url}/charge?{urlencode({"loan": loan_id})}'
        http_request = Request(url, method='POST')

        try:
            with url_request.urlopen(http_request) as response:
                body = response.read().decode('utf-8', errors='replace')
                return GatewayResponse(response.status, body)
        except HTTPError as response:
            body = response.read().decode('utf-8', errors='replace')
            return GatewayResponse(response.code, body)
        except InterruptedError as error:
            raise PaymentGatewayInterrupted('payment gateway call interrupted') from error
        except (OSError, URLError) as error:
            raise PaymentGatewayUnavailable('payment gateway unavailable') from error
