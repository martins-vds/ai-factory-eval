import os
import urllib.error
import urllib.request

from .services import GatewayResponse

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class GatewayFailure(Exception):
    pass


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
        request = urllib.request.Request(
            f'{gateway_url}/charge?loan={loan_id}',
            method='POST',
        )
        try:
            with urllib.request.urlopen(request) as response:
                return GatewayResponse(
                    status_code=response.status,
                    body=response.read().decode('utf-8', errors='replace'),
                )
        except urllib.error.HTTPError as response:
            return GatewayResponse(
                status_code=response.code,
                body=response.read().decode('utf-8', errors='replace'),
            )
        except InterruptedError as error:
            raise GatewayFailure('payment gateway interrupted') from error
        except urllib.error.URLError as error:
            raise GatewayFailure('payment gateway unavailable') from error
        except OSError as error:
            raise GatewayFailure('payment gateway unavailable') from error
