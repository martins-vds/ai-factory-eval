import os
from urllib import error, request

from .services import GatewayResponse, InterruptedPayment, PaymentGatewayFailure

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
        payment_request = request.Request(
            f'{gateway_url}/charge?loan={loan_id}',
            data=b'',
            method='POST',
        )

        try:
            with request.urlopen(payment_request) as response:
                status = response.status
                body = response.read().decode('utf-8')
        except error.HTTPError as response:
            status = response.code
            body = response.read().decode('utf-8')
        except InterruptedError as exc:
            raise InterruptedPayment('payment request interrupted') from exc
        except error.URLError as exc:
            if isinstance(exc.reason, InterruptedError):
                raise InterruptedPayment('payment request interrupted') from exc.reason
            raise PaymentGatewayFailure('payment gateway unavailable') from exc
        except OSError as exc:
            raise PaymentGatewayFailure('payment gateway unavailable') from exc

        return GatewayResponse(200 if status == 200 else 502, body)
