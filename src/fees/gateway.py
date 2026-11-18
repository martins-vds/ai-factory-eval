import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .services import PaymentResult


class PaymentInterrupted(Exception):
    pass


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> PaymentResult:
        base_url = os.environ.get(
            'PAYMENT_GATEWAY_URL',
            'https://payments.lending-library.invalid',
        )
        url = f'{base_url.rstrip("/")}/charge?{urlencode({"loan": loan_id})}'
        request = Request(url, data=b'', method='POST')

        try:
            with urlopen(request) as response:
                status = response.status
                body = response.read().decode()
        except HTTPError as error:
            return PaymentResult(502, error.read().decode())
        except InterruptedError as error:
            raise PaymentInterrupted('payment gateway request was interrupted') from error
        except URLError as error:
            if isinstance(error.reason, InterruptedError):
                raise PaymentInterrupted(
                    'payment gateway request was interrupted'
                ) from error.reason
            return PaymentResult(502, 'payment gateway unavailable\n')
        except OSError:
            return PaymentResult(502, 'payment gateway unavailable\n')

        return PaymentResult(200 if status == 200 else 502, body)
