import os
import urllib.error
import urllib.request

from .services import (
    GatewayResponse,
    PaymentGatewayInterrupted,
    PaymentGatewayUnavailable,
)


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        return None


class HttpPaymentGateway:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url
        self.opener = urllib.request.build_opener(_NoRedirectHandler())

    @staticmethod
    def _raise_gateway_failure(error):
        cause = error.reason if isinstance(error, urllib.error.URLError) else error
        if isinstance(cause, InterruptedError):
            raise PaymentGatewayInterrupted from cause
        raise PaymentGatewayUnavailable from error

    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = self.base_url or os.environ.get(
            'PAYMENT_GATEWAY_URL',
            'https://payments.lending-library.invalid',
        )
        request = urllib.request.Request(
            f'{gateway_url}/charge?loan={loan_id}',
            data=b'',
            method='POST',
        )

        try:
            with self.opener.open(request) as response:
                return GatewayResponse(
                    response.status, response.read().decode('utf-8', errors='replace')
                )
        except urllib.error.HTTPError as response:
            try:
                with response:
                    body = response.read().decode('utf-8', errors='replace')
            except (urllib.error.URLError, OSError) as error:
                self._raise_gateway_failure(error)
            return GatewayResponse(response.code, body)
        except (urllib.error.URLError, OSError) as error:
            self._raise_gateway_failure(error)
