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


class GatewayFailure(Exception):
    pass


@dataclass(frozen=True)
class GatewayResult:
    status_code: int
    body: str


@dataclass(frozen=True)
class PaymentResult:
    status_code: int
    body: str
    failure: GatewayFailure | None = None


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResult: ...


@dataclass(frozen=True)
class LateFee:
    loan_id: str
    due_on: date
    late_days: int
    fee_cents: int


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def calculate(self, loan_id: str) -> LateFee | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        late_days = max(0, (end_date - loan.due_on).days)
        fee_cents = 0 if late_days <= 2 else min(1000, late_days * 25)
        return LateFee(loan.id, loan.due_on, late_days, fee_cents)


class PaymentApplication:
    def __init__(self, repository: LoanRepository, gateway: PaymentGateway):
        self.repository = repository
        self.gateway = gateway

    def pay(self, loan_id: str) -> PaymentResult | None:
        if self.repository.find(loan_id) is None:
            return None
        try:
            result = self.gateway.charge(loan_id)
        except GatewayFailure as failure:
            return PaymentResult(502, 'payment gateway unavailable\n', failure)
        status = 200 if result.status_code == 200 else 502
        return PaymentResult(status, result.body)
