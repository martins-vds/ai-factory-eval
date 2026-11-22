import os
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .services import GatewayResponse


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = os.environ.get(
            'PAYMENT_GATEWAY_URL',
            'https://payments.lending-library.invalid',
        )
        request = Request(
            f'{gateway_url}/charge?loan={quote(loan_id, safe="")}',
            method='POST',
        )
        try:
            with urlopen(request) as response:
                return GatewayResponse(response.status, response.read().decode('utf-8'))
        except HTTPError as response:
            return GatewayResponse(response.code, response.read().decode('utf-8'))
