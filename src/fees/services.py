from dataclasses import dataclass
from datetime import date
from typing import Protocol


@dataclass(frozen=True)
class FeeQuote:
    late_days: int
    amount_cents: int


class LoanRecord(Protocol):
    id: str
    member: str
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def find(self, loan_id: str) -> LoanRecord | None: ...


class Clock(Protocol):
    def today(self) -> date: ...


@dataclass(frozen=True)
class GatewayResponse:
    status: int
    body: bytes


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


class GatewayUnavailable(Exception):
    def __init__(self, body=b'payment gateway unavailable\n'):
        self.body = body
        super().__init__(body.decode('utf-8', errors='replace'))


class PaymentFailed(Exception):
    def __init__(self, body):
        self.body = body
        super().__init__(body.decode('utf-8', errors='replace'))


@dataclass(frozen=True)
class LoanFee:
    loan: LoanRecord
    quote: FeeQuote


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def quote(self, loan_id: str) -> LoanFee | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None
        quote = calculate_late_fee(loan.due_on, loan.returned_on, self.clock.today())
        return LoanFee(loan=loan, quote=quote)


class PaymentApplication:
    def __init__(self, repository: LoanRepository, gateway: PaymentGateway):
        self.repository = repository
        self.gateway = gateway

    def pay(self, loan_id: str) -> GatewayResponse | None:
        if self.repository.find(loan_id) is None:
            return None
        try:
            response = self.gateway.charge(loan_id)
        except GatewayUnavailable as error:
            cause = error.__cause__ or error
            raise PaymentFailed(error.body) from cause
        if response.status != 200:
            raise PaymentFailed(response.body)
        return response


def calculate_late_fee(due_on: date, returned_on: date | None, today: date) -> FeeQuote:
    late_days = max(0, ((returned_on or today) - due_on).days)
    amount_cents = 0 if late_days <= 2 else min(late_days * 25, 1000)
    return FeeQuote(late_days=late_days, amount_cents=amount_cents)
