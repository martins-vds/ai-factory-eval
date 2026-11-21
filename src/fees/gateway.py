import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class HttpPaymentGateway:
    def charge(self, loan_id):
        base_url = os.environ.get(
            'PAYMENT_GATEWAY_URL',
            'https://payments.lending-library.invalid',
        )
        url = f'{base_url.rstrip("/")}/charge?{urlencode({"loan": loan_id})}'
        request = Request(url, data=b'', method='POST')
        try:
            with urlopen(request, timeout=5) as response:
                return response.status, response.read().decode('utf-8')
        except HTTPError as response:
            return response.code, response.read().decode('utf-8')
        except (URLError, TimeoutError, InterruptedError, OSError) as error:
            raise InterruptedError('payment gateway interrupted') from error
