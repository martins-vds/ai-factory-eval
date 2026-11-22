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
class GatewayResponse:
    status_code: int
    body: str


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


class LoanNotFound(Exception):
    pass


class PaymentGatewayUnavailable(Exception):
    pass


class PaymentGatewayInterrupted(PaymentGatewayUnavailable):
    pass


@dataclass(frozen=True)
class LateFee:
    loan: LoanRecord
    days_late: int
    amount_cents: int


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def fee_for(self, loan_id: str) -> LateFee:
        loan = self.repository.find(loan_id)
        if loan is None:
            raise LoanNotFound(loan_id)

        end_date = loan.returned_on or self.clock.today()
        days_late = max((end_date - loan.due_on).days, 0)
        amount_cents = min(days_late * 25, 1000) if days_late > 2 else 0
        return LateFee(loan, days_late, amount_cents)


@dataclass(frozen=True)
class PaymentResult:
    status_code: int
    body: str


class PaymentApplication:
    def __init__(self, repository: LoanRepository, gateway: PaymentGateway):
        self.repository = repository
        self.gateway = gateway

    def pay(self, loan_id: str) -> PaymentResult:
        if self.repository.find(loan_id) is None:
            raise LoanNotFound(loan_id)

        try:
            response = self.gateway.charge(loan_id)
        except PaymentGatewayInterrupted:
            raise
        except PaymentGatewayUnavailable:
            return PaymentResult(502, 'payment gateway unavailable\n')

        status_code = 200 if response.status_code == 200 else 502
        return PaymentResult(status_code, response.body)
