import logging
import os
import urllib.request
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

logger = logging.getLogger(__name__)
DEFAULT_PAYMENT_GATEWAY_URL = 'http://localhost:8081'


@dataclass(frozen=True)
class GatewayResponse:
    status: int
    body: bytes


def charge_loan(loan_id: str) -> GatewayResponse:
    gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_PAYMENT_GATEWAY_URL).rstrip('/')
    request = urllib.request.Request(
        f'{gateway_url}/charge?{urlencode({"loan": loan_id})}',
        data=b'',
        method='POST',
    )

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return GatewayResponse(response.status, response.read())
    except HTTPError as error:
        return GatewayResponse(error.code, error.read())
    except InterruptedError:
        logger.exception('Payment gateway request was interrupted')
        return GatewayResponse(0, b'payment gateway unavailable\n')
    except URLError as error:
        if isinstance(error.reason, InterruptedError):
            logger.error(
                'Payment gateway request was interrupted',
                exc_info=(type(error.reason), error.reason, error.reason.__traceback__),
            )
        return GatewayResponse(0, b'payment gateway unavailable\n')
    except OSError:
        return GatewayResponse(0, b'payment gateway unavailable\n')
