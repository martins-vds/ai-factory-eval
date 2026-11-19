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


@dataclass(frozen=True)
class PaymentGatewayResponse:
    status_code: int
    body: str


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> PaymentGatewayResponse: ...


class PaymentGatewayError(Exception):
    pass


@dataclass(frozen=True)
class LateFee:
    loan_id: str
    due_on: date
    late_days: int
    amount_cents: int


class LateFeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def calculate(self, loan_id: str) -> LateFee | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        actual_on = loan.returned_on or self.clock.today()
        late_days = max(0, (actual_on - loan.due_on).days)
        amount_cents = 0 if late_days <= 2 else min(1000, late_days * 25)
        return LateFee(loan.id, loan.due_on, late_days, amount_cents)


@dataclass(frozen=True)
class PaymentResult:
    status_code: int
    body: str


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
