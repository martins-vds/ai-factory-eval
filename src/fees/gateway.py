import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .services import GatewayResponse, GatewayUnavailable


class HttpPaymentGateway:
    def __init__(self, base_url=None):
        self.base_url = base_url

    def charge(self, loan_id: str) -> GatewayResponse:
        base_url = self.base_url or os.environ.get(
            'PAYMENT_GATEWAY_URL',
            'https://payments.lending-library.invalid',
        )
        request = Request(f'{base_url.rstrip("/")}/charge?loan={loan_id}', method='POST')

        try:
            with urlopen(request) as response:
                return GatewayResponse(
                    response.status,
                    response.read().decode('utf-8'),
                )
        except HTTPError as response:
            return GatewayResponse(
                response.code,
                response.read().decode('utf-8'),
            )
        except URLError as exc:
            if isinstance(exc.reason, InterruptedError):
                raise exc.reason from exc
            raise GatewayUnavailable() from exc
        except InterruptedError:
            raise
        except OSError as exc:
            raise GatewayUnavailable() from exc
