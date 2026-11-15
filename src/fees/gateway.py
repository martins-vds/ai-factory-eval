import os
from dataclasses import dataclass
from urllib.error import HTTPError
from urllib.request import Request, urlopen


DEFAULT_PAYMENT_GATEWAY_URL = 'https://payments.lending-library.invalid'


@dataclass(frozen=True)
class GatewayResponse:
    status: int
    body: str


class PaymentGatewayError(Exception):
    pass


class PaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_PAYMENT_GATEWAY_URL)
        request = Request(
            f'{gateway_url}/charge?loan={loan_id}',
            data=b'',
            method='POST',
        )
        try:
            with urlopen(request) as response:
                return GatewayResponse(response.status, response.read().decode())
        except HTTPError as error:
            return GatewayResponse(error.code, error.read().decode())
        except InterruptedError as error:
            raise PaymentGatewayError('payment gateway unavailable') from error
        except OSError as error:
            raise PaymentGatewayError('payment gateway unavailable') from error
