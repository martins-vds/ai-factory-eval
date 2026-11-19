import os
from urllib import error, request
from urllib.parse import quote

from .services import GatewayResult


class GatewayFailure(Exception):
    pass


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResult:
        gateway_url = os.environ.get(
            'PAYMENT_GATEWAY_URL',
            'https://payments.lending-library.invalid',
        )
        url = f'{gateway_url}/charge?loan={quote(loan_id, safe="")}'
        outbound_request = request.Request(url, data=b'', method='POST')
        try:
            with request.urlopen(outbound_request) as response:
                return GatewayResult(response.status, response.read().decode('utf-8'))
        except error.HTTPError as response:
            return GatewayResult(response.code, response.read().decode('utf-8'))
        except InterruptedError as interruption:
            raise GatewayFailure('payment gateway unavailable') from interruption
        except error.URLError as failure:
            interruption = failure.reason if isinstance(failure.reason, InterruptedError) else failure
            raise GatewayFailure('payment gateway unavailable') from interruption
        except OSError as failure:
            raise GatewayFailure('payment gateway unavailable') from failure
