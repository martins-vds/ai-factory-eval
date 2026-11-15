import os
from dataclasses import dataclass
from http.client import HTTPException
from urllib.error import HTTPError
from urllib.request import Request, urlopen

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


@dataclass(frozen=True)
class PaymentResponse:
    status_code: int
    body: str


class PaymentGatewayUnavailable(Exception):
    pass


class HttpPaymentGateway:
    def __init__(self, base_url=None):
        self.base_url = base_url

    def charge(self, loan_id: str) -> PaymentResponse:
        base_url = self.base_url or os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
        request = Request(f'{base_url}/charge?loan={loan_id}', method='POST')
        try:
            with urlopen(request) as response:
                body = response.read().decode('utf-8', errors='replace')
                return PaymentResponse(200 if response.status == 200 else 502, body)
        except HTTPError as response:
            try:
                body = response.read().decode('utf-8', errors='replace')
            except (OSError, HTTPException) as error:
                raise PaymentGatewayUnavailable from error
            return PaymentResponse(502, body)
        except (OSError, HTTPException) as error:
            raise PaymentGatewayUnavailable from error
