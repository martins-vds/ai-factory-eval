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


class GatewayResponse(Protocol):
    status_code: int
    body: str


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


@dataclass(frozen=True)
class FeeQuote:
    loan_id: str
    due_on: date
    days_late: int
    amount_cents: int


@dataclass(frozen=True)
class PaymentResult:
    status_code: int
    body: str


class PaymentGatewayUnavailable(Exception):
    pass


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def calculate(self, loan_id: str) -> FeeQuote | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on if loan.returned_on is not None else self.clock.today()
        days_late = max(0, (end_date - loan.due_on).days)
        amount_cents = 0 if days_late <= 2 else min(1000, days_late * 25)
        return FeeQuote(loan.id, loan.due_on, days_late, amount_cents)


class PaymentApplication:
    def __init__(self, repository: LoanRepository, gateway: PaymentGateway):
        self.repository = repository
        self.gateway = gateway

    def pay(self, loan_id: str) -> PaymentResult:
        if self.repository.find(loan_id) is None:
            return PaymentResult(404, 'no such loan\n')

        try:
            response = self.gateway.charge(loan_id)
        except OSError as error:
            raise PaymentGatewayUnavailable from error

        status_code = 200 if response.status_code == 200 else 502
        return PaymentResult(status_code, response.body)
