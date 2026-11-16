import os
import urllib.request
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from .services import (
    GatewayResponse,
    PaymentGatewayInterrupted,
    PaymentGatewayUnavailable,
)

DEFAULT_PAYMENT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class HttpPaymentGateway:
    def charge(self, loan_id):
        gateway_url = os.environ.get(
            'PAYMENT_GATEWAY_URL',
            DEFAULT_PAYMENT_GATEWAY_URL,
        )
        query = urlencode({'loan': loan_id})
        request = urllib.request.Request(
            f'{gateway_url}/charge?{query}',
            data=b'',
            method='POST',
        )
        try:
            with urllib.request.urlopen(request) as response:
                return GatewayResponse(response.status, response.read())
        except HTTPError as error:
            return GatewayResponse(error.code, error.read())
        except InterruptedError as error:
            raise PaymentGatewayInterrupted from error
        except URLError as error:
            if isinstance(error.reason, InterruptedError):
                raise PaymentGatewayInterrupted from error.reason
            raise PaymentGatewayUnavailable from error
        except (HTTPException, OSError) as error:
            raise PaymentGatewayUnavailable from error
