import os
from urllib import error, request

from .services import PaymentResponse


class PaymentGatewayUnavailable(Exception):
    pass


class HttpPaymentGateway:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url

    def charge(self, loan_id: str) -> PaymentResponse:
        base_url = self.base_url or os.environ.get(
            'PAYMENT_GATEWAY_URL',
            'https://payments.lending-library.invalid',
        )
        req = request.Request(
            f'{base_url}/charge?loan={loan_id}',
            data=b'',
            method='POST',
        )
        try:
            with request.urlopen(req, timeout=10) as response:
                status = response.status
                body = response.read().decode('utf-8')
        except error.HTTPError as response:
            with response:
                body = response.read().decode('utf-8')
            return PaymentResponse(502, body)
        except OSError as cause:
            raise PaymentGatewayUnavailable('payment gateway unavailable') from cause

        return PaymentResponse(200 if status == 200 else 502, body)
