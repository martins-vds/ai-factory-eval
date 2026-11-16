import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


@dataclass
class GatewayResponse:
    status_code: int
    body: str


class PaymentGatewayUnavailable(Exception):
    pass


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        base_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
        url = f'{base_url}/charge?{urlencode({"loan": loan_id})}'
        request = Request(url, data=b'', method='POST')

        try:
            with urlopen(request) as response:
                return GatewayResponse(
                    status_code=response.status,
                    body=response.read().decode('utf-8'),
                )
        except HTTPError as response:
            return GatewayResponse(
                status_code=response.code,
                body=response.read().decode('utf-8'),
            )
        except (URLError, OSError) as error:
            cause = (
                error.reason
                if isinstance(error, URLError) and isinstance(error.reason, BaseException)
                else error
            )
            raise PaymentGatewayUnavailable('payment gateway unavailable') from cause
