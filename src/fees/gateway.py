import os
from dataclasses import dataclass
from urllib import error, request


DEFAULT_GATEWAY_URL = 'https://payments.lending-library.invalid'


@dataclass(frozen=True)
class GatewayResponse:
    status_code: int
    body: str


class NoRedirectHandler(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, new_url):
        return None


class PaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_GATEWAY_URL)
        charge_url = f'{gateway_url}/charge?loan={loan_id}'
        outbound_request = request.Request(charge_url, method='POST')
        opener = request.build_opener(NoRedirectHandler)

        try:
            with opener.open(outbound_request) as response:
                body = response.read().decode()
                status_code = 200 if response.status == 200 else 502
                return GatewayResponse(status_code, body)
        except error.HTTPError as exc:
            return GatewayResponse(502, exc.read().decode())
        except InterruptedError:
            raise
        except error.URLError as exc:
            if isinstance(exc.reason, InterruptedError):
                raise exc.reason from exc
            return GatewayResponse(502, 'payment gateway unavailable\n')
        except OSError:
            return GatewayResponse(502, 'payment gateway unavailable\n')
