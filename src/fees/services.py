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


@dataclass(frozen=True)
class GatewayResponse:
    status: int
    body: bytes


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


@dataclass(frozen=True)
class LateFee:
    loan_id: str
    due_on: date
    days_late: int
    amount_cents: int


class FeeApplication:
    def __init__(self, loans: LoanRepository, clock: Clock):
        self.loans = loans
        self.clock = clock

    def calculate(self, loan_id: str) -> LateFee | None:
        loan = self.loans.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        days_late = max(0, (end_date - loan.due_on).days)
        amount_cents = min(1000, days_late * 25) if days_late > 2 else 0
        return LateFee(loan.id, loan.due_on, days_late, amount_cents)


@dataclass(frozen=True)
class PaymentResult:
    status: int
    body: bytes
    interruption: InterruptedError | None = None


class PaymentApplication:
    def __init__(self, loans: LoanRepository, gateway: PaymentGateway):
        self.loans = loans
        self.gateway = gateway

    def pay(self, loan_id: str) -> PaymentResult:
        if self.loans.find(loan_id) is None:
            return PaymentResult(404, b'no such loan\n')

        try:
            response = self.gateway.charge(loan_id)
        except InterruptedError as error:
            return PaymentResult(502, b'payment gateway unavailable\n', error)
        except OSError:
            return PaymentResult(502, b'payment gateway unavailable\n')

        status = 200 if response.status == 200 else 502
        return PaymentResult(status, response.body)
