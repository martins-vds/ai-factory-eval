import logging
import os
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LateFee:
    days_late: int
    amount: Decimal


@dataclass(frozen=True)
class PaymentResult:
    status_code: int
    body: bytes


def calculate_late_fee(loan, today: date | None = None) -> LateFee:
    assessed_on = loan.returned_on or today or timezone.localdate()
    days_late = max(0, (assessed_on - loan.due_on).days)
    fee_cents = min(max(days_late - 2, 0) * 25, 1000)
    return LateFee(days_late, Decimal(fee_cents) / 100)


def charge_late_fee(loan_id: str) -> PaymentResult:
    gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', 'http://127.0.0.1:8081').rstrip('/')
    request = Request(
        f'{gateway_url}/charge?loan={quote(loan_id, safe="")}',
        data=b'',
        method='POST',
    )
    try:
        with urlopen(request, timeout=5) as response:
            status_code = response.status
            body = response.read()
    except HTTPError as error:
        status_code = error.code
        body = error.read()
    except InterruptedError:
        logger.warning('Payment gateway request was interrupted', exc_info=True)
        return PaymentResult(502, b'payment gateway unavailable\n')
    except (URLError, OSError):
        return PaymentResult(502, b'payment gateway unavailable\n')

    return PaymentResult(status_code if status_code == 200 else 502, body)
