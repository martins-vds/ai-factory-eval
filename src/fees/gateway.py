import os
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class PaymentInterrupted(Exception):
    pass


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        return None


def charge_loan_fee(loan_id: str) -> tuple[int, str]:
    gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
    url = f'{gateway_url}/charge?{urlencode({"loan": loan_id})}'
    request = Request(url, data=b'', method='POST')
    opener = build_opener(NoRedirectHandler())

    try:
        with opener.open(request) as response:
            return response.status, response.read().decode('utf-8')
    except HTTPError as response:
        return response.code, response.read().decode('utf-8')
    except InterruptedError as error:
        raise PaymentInterrupted('payment gateway request was interrupted') from error
    except OSError:
        return 502, 'payment gateway unavailable\n'
