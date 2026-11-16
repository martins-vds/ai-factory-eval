import os
from dataclasses import dataclass
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from src.loans.services import LoanRecord

DEFAULT_PAYMENT_GATEWAY_URL = 'https://payments.lending-library.invalid'


@dataclass
class GatewayResponse:
    status_code: int
    body: str


class PaymentGatewayUnavailable(Exception):
    pass


class LoanLookup(Protocol):
    def find(self, loan_id: str) -> LoanRecord | None: ...


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        return None


class HttpPaymentGateway:
    def charge(self, loan_id: str) -> GatewayResponse:
        gateway_url = os.environ.get('PAYMENT_GATEWAY_URL', DEFAULT_PAYMENT_GATEWAY_URL)
        url = f'{gateway_url}/charge?{urlencode({"loan": loan_id})}'
        request = Request(url, data=b'', method='POST')
        opener = build_opener(NoRedirectHandler)

        try:
            try:
                with opener.open(request) as response:
                    status_code = response.status
                    body = response.read()
            except HTTPError as response:
                return GatewayResponse(
                    status_code=502,
                    body=response.read().decode('utf-8', errors='replace'),
                )
        except (OSError, URLError) as error:
            raise PaymentGatewayUnavailable from error

        return GatewayResponse(
            status_code=200 if status_code == 200 else 502,
            body=body.decode('utf-8', errors='replace'),
        )


class PaymentApplication:
    def __init__(self, loans: LoanLookup, gateway: PaymentGateway):
        self.loans = loans
        self.gateway = gateway

    def pay(self, loan_id: str) -> GatewayResponse | None:
        if self.loans.find(loan_id) is None:
            return None
        return self.gateway.charge(loan_id)
