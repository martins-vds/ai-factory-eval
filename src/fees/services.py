from dataclasses import dataclass
from datetime import date
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    due_on: date
    returned_on: date | None


class FeeRepository(Protocol):
    def find(self, loan_id: str) -> LoanRecord | None: ...


class Clock(Protocol):
    def today(self) -> date: ...


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> tuple[int, bytes]: ...


@dataclass(frozen=True)
class FeeQuote:
    loan: LoanRecord
    late_days: int
    amount_cents: int


@dataclass(frozen=True)
class PaymentResult:
    status_code: int
    body: bytes


class FeeApplication:
    def __init__(self, repository: FeeRepository, clock: Clock, gateway: PaymentGateway):
        self.repository = repository
        self.clock = clock
        self.gateway = gateway

    def quote(self, loan_id: str) -> FeeQuote | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        late_days = max(0, (end_date - loan.due_on).days)
        amount_cents = min(max(late_days - 2, 0) * 25, 1000)
        return FeeQuote(loan, late_days, amount_cents)

    def pay(self, loan_id: str) -> PaymentResult | None:
        if self.repository.find(loan_id) is None:
            return None

        status_code, body = self.gateway.charge(loan_id)
        return PaymentResult(200 if status_code == 200 else 502, body)
