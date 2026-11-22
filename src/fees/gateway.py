import os
from urllib import error, request

from .services import GatewayResponse, InterruptedPayment, PaymentGatewayFailure

DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


class _NoRedirectHandler(request.HTTPRedirectHandler):
    def redirect_request(self, _request, _file, _code, _message, _headers, _url):
        return None


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
        payment_request = request.Request(
            f'{gateway_url}/charge?loan={loan_id}',
            data=b'',
            method='POST',
        )

        try:
            opener = request.build_opener(_NoRedirectHandler)
            with opener.open(payment_request) as response:
                status = response.status
                body = response.read().decode('utf-8', errors='replace')
        except error.HTTPError as response:
            status = response.code
            body = response.read().decode('utf-8', errors='replace')
        except InterruptedError as exc:
            raise InterruptedPayment from exc
        except error.URLError as exc:
            if isinstance(exc.reason, InterruptedError):
                raise InterruptedPayment from exc.reason
            raise PaymentGatewayFailure from exc
        except OSError as exc:
            raise PaymentGatewayFailure from exc

        return GatewayResponse(status, body)
