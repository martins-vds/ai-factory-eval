import os
from http.client import HTTPException
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .services import GatewayResponse


def _read_body(response):
    try:
        return response.read()
    except HTTPException as error:
        raise OSError('incomplete payment gateway response') from error


class HttpPaymentGateway:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.environ.get(
            'PAYMENT_GATEWAY_URL',
            'https://payments.lending-library.invalid',
        )

    def charge(self, loan_id: str) -> GatewayResponse:
        url = f'{self.base_url.rstrip("/")}/charge?loan={quote(loan_id, safe="")}'
        request = Request(url, data=b'', method='POST')
        try:
            with urlopen(request, timeout=5) as response:
                return GatewayResponse(response.status, _read_body(response))
        except HTTPError as response:
            return GatewayResponse(response.code, _read_body(response))
