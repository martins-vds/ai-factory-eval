import os
from datetime import date
from dataclasses import dataclass
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


def _open_gateway(request):
    return build_opener(_NoRedirect()).open(request)


def calculate_late_fee(due_on: date, through: date) -> tuple[int, Decimal]:
    days_late = max((through - due_on).days, 0)
    fee_cents = min(days_late * 25, 1000) if days_late > 2 else 0
    return days_late, Decimal(fee_cents) / Decimal(100)


@dataclass(frozen=True)
class PaymentResult:
    status_code: int
    body: str
    interruption: InterruptedError | None = None


def pay_late_fee(loan_id: str) -> PaymentResult:
    gateway = os.environ.get(
        'PAYMENT_GATEWAY_URL', 'https://payments.lending-library.invalid'
    )
    request = Request(
        f'{gateway}/charge?{urlencode({"loan": loan_id})}',
        method='POST',
    )

    try:
        with _open_gateway(request) as response:
            return PaymentResult(
                200 if response.status == 200 else 502,
                response.read().decode('utf-8', errors='replace'),
            )
    except HTTPError as error:
        return PaymentResult(
            502,
            error.read().decode('utf-8', errors='replace'),
        )
    except InterruptedError as error:
        return PaymentResult(502, 'payment gateway unavailable\n', error)
    except (OSError, URLError):
        return PaymentResult(502, 'payment gateway unavailable\n')
