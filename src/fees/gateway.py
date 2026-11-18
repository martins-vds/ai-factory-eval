import os
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings

from .services import GatewayResponse


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        base_url = getattr(
            settings,
            'PAYMENT_GATEWAY_URL',
            os.environ.get('PAYMENT_GATEWAY_URL', 'http://localhost:9999'),
        )
        url = f'{base_url.rstrip("/")}/charge?{urlencode({"loan": loan_id})}'
        request = Request(url, method='POST')

        try:
            with urlopen(request) as response:
                return GatewayResponse(response.status, response.read())
        except HTTPError as response:
            return GatewayResponse(response.code, response.read())
