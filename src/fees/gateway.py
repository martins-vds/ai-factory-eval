import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .services import GatewayUnavailable


@dataclass(frozen=True)
class GatewayResult:
    status_code: int
    body: str


class HttpPaymentGateway:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url

    def charge(self, loan_id: str) -> GatewayResult:
        base_url = self.base_url or os.environ.get(
            'PAYMENT_GATEWAY_URL',
            'https://payments.lending-library.invalid',
        )
        request = Request(f'{base_url}/charge?loan={loan_id}', method='POST')
        try:
            with urlopen(request) as response:
                return GatewayResult(response.status, response.read().decode())
        except HTTPError as response:
            return GatewayResult(response.code, response.read().decode())
        except (URLError, OSError) as error:
            raise GatewayUnavailable('payment gateway unavailable\n') from error
