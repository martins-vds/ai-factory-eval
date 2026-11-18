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
    body: str


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


@dataclass(frozen=True)
class LateFee:
    loan_id: str
    due_on: date
    late_days: int
    amount_cents: int

    @property
    def formatted_amount(self) -> str:
        return f'{self.amount_cents // 100}.{self.amount_cents % 100:02d}'


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def calculate(self, loan_id: str) -> LateFee | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        late_days = max(0, ((loan.returned_on or self.clock.today()) - loan.due_on).days)
        amount_cents = 0 if late_days <= 2 else min(late_days * 25, 1000)
        return LateFee(loan.id, loan.due_on, late_days, amount_cents)


@dataclass(frozen=True)
class PaymentResult:
    status: int
    body: str
    failure: Exception | None = None


class PaymentApplication:
    def __init__(self, repository: LoanRepository, gateway: PaymentGateway):
        self.repository = repository
        self.gateway = gateway

    def charge(self, loan_id: str) -> PaymentResult:
        if self.repository.find(loan_id) is None:
            return PaymentResult(404, 'no such loan\n')

        try:
            response = self.gateway.charge(loan_id)
        except InterruptedError as error:
            return PaymentResult(502, 'payment gateway unavailable\n', error)
        except OSError as error:
            return PaymentResult(502, 'payment gateway unavailable\n', error)

        return PaymentResult(200 if response.status == 200 else 502, response.body)
