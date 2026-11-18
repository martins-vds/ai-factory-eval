from dataclasses import dataclass
from datetime import date
from typing import Protocol


class Loan(Protocol):
    id: str
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def find(self, loan_id: str) -> Loan | None: ...


class Clock(Protocol):
    def today(self) -> date: ...


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> 'GatewayResponse': ...


@dataclass(frozen=True)
class LateFee:
    days_late: int
    amount_cents: int


@dataclass(frozen=True)
class GatewayResponse:
    status_code: int
    body: str


@dataclass(frozen=True)
class FeeQuote:
    loan: Loan
    days_late: int
    amount_cents: int


def calculate_late_fee(*, due_on: date, returned_on: date | None, today: date) -> LateFee:
    end_date = returned_on or today
    days_late = max(0, (end_date - due_on).days)
    amount_cents = 0 if days_late <= 2 else min(1000, days_late * 25)
    return LateFee(days_late=days_late, amount_cents=amount_cents)


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def quote(self, loan_id: str) -> FeeQuote | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        fee = calculate_late_fee(
            due_on=loan.due_on,
            returned_on=loan.returned_on,
            today=self.clock.today(),
        )
        return FeeQuote(loan=loan, days_late=fee.days_late, amount_cents=fee.amount_cents)


class PaymentApplication:
    def __init__(self, repository: LoanRepository, gateway: PaymentGateway):
        self.repository = repository
        self.gateway = gateway

    def charge(self, loan_id: str) -> GatewayResponse | None:
        if self.repository.find(loan_id) is None:
            return None
        return self.gateway.charge(loan_id)
