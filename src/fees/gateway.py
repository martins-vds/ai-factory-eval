import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


@dataclass(frozen=True)
class PaymentResponse:
    status: int
    body: str


class PaymentGatewayError(Exception):
    pass


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        return None


def charge_loan(loan_id: str) -> PaymentResponse:
    gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
    request = Request(
        f'{gateway_url}/charge?{urlencode({"loan": loan_id})}',
        method='POST',
    )
    opener = build_opener(NoRedirectHandler)

    try:
        with opener.open(request) as response:
            status = response.status
            body = response.read().decode('utf-8', errors='replace')
    except HTTPError as response:
        try:
            with response:
                body = response.read().decode('utf-8', errors='replace')
        except InterruptedError as error:
            raise PaymentGatewayError('payment gateway unavailable') from error
        except (URLError, OSError) as error:
            raise PaymentGatewayError('payment gateway unavailable') from error
        status = response.code
    except InterruptedError as error:
        raise PaymentGatewayError('payment gateway unavailable') from error
    except (URLError, OSError) as error:
        raise PaymentGatewayError('payment gateway unavailable') from error

    return PaymentResponse(status if status == 200 else 502, body)
