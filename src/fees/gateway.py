import os
import urllib.error
import urllib.request

from .services import (
    GatewayResponse,
    PaymentGatewayInterrupted,
    PaymentGatewayUnavailable,
)


class HttpPaymentGateway:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url

    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = self.base_url or os.environ.get(
            'PAYMENT_GATEWAY_URL',
            'https://payments.lending-library.invalid',
        )
        request = urllib.request.Request(
            f'{gateway_url}/charge?loan={loan_id}',
            data=b'',
            method='POST',
        )

        try:
            with urllib.request.urlopen(request) as response:
                return GatewayResponse(
                    response.status, response.read().decode('utf-8', errors='replace')
                )
        except InterruptedError as error:
            raise PaymentGatewayInterrupted('payment request interrupted') from error
        except urllib.error.HTTPError as response:
            with response:
                body = response.read().decode('utf-8', errors='replace')
            return GatewayResponse(response.code, body)
        except urllib.error.URLError as error:
            if isinstance(error.reason, InterruptedError):
                raise PaymentGatewayInterrupted('payment request interrupted') from error.reason
            raise PaymentGatewayUnavailable('payment gateway unavailable') from error
        except OSError as error:
            raise PaymentGatewayUnavailable('payment gateway unavailable') from error
