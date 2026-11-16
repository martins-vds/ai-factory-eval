import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings


class PaymentGatewayUnavailable(Exception):
    pass


class HttpPaymentGateway:
    def charge(self, loan_id):
        base_url = getattr(
            settings,
            'PAYMENT_GATEWAY_URL',
            os.environ.get('PAYMENT_GATEWAY_URL', 'http://localhost:8081'),
        )
        url = f'{base_url.rstrip("/")}/charge?{urlencode({"loan": loan_id})}'
        request = Request(url, data=b'', method='POST')

        try:
            with urlopen(request, timeout=5) as response:
                return response.status, response.read()
        except HTTPError as response:
            try:
                return response.code, response.read()
            except OSError as cause:
                raise PaymentGatewayUnavailable from cause
        except InterruptedError as cause:
            raise PaymentGatewayUnavailable from cause
        except URLError as error:
            cause = error.reason if isinstance(error.reason, InterruptedError) else error
            raise PaymentGatewayUnavailable from cause
        except OSError as cause:
            raise PaymentGatewayUnavailable from cause
