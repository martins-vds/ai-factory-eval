from dataclasses import dataclass
from datetime import date
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def find(self, loan_id: str) -> LoanRecord | None: ...


class Clock(Protocol):
    def today(self) -> date: ...


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> 'GatewayResponse': ...


@dataclass(frozen=True)
class FeeQuote:
    loan: LoanRecord
    days_late: int
    fee_cents: int


@dataclass(frozen=True)
class GatewayResponse:
    status_code: int
    body: str


@dataclass(frozen=True)
class PaymentResult:
    status_code: int
    body: str


class PaymentGatewayError(Exception):
    pass


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def calculate_fee(self, loan_id: str) -> FeeQuote | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        days_late = max(0, (end_date - loan.due_on).days)
        fee_cents = 0 if days_late <= 2 else min(1000, days_late * 25)
        return FeeQuote(loan, days_late, fee_cents)


class PaymentApplication:
    def __init__(self, repository: LoanRepository, gateway: PaymentGateway):
        self.repository = repository
        self.gateway = gateway

    def pay(self, loan_id: str) -> PaymentResult | None:
        if self.repository.find(loan_id) is None:
            return None

        response = self.gateway.charge(loan_id)
        status_code = 200 if response.status_code == 200 else 502
        return PaymentResult(status_code, response.body)
