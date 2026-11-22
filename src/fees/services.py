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
class FeeQuote:
    loan: LoanRecord
    late_days: int
    amount_cents: int

    @property
    def amount(self):
        return f'${self.amount_cents // 100}.{self.amount_cents % 100:02d}'


@dataclass(frozen=True)
class GatewayResponse:
    status: int
    body: bytes


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


@dataclass(frozen=True)
class PaymentResult:
    status: int
    body: bytes
    interruption: InterruptedError | None = None


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def calculate(self, loan_id: str) -> FeeQuote | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        late_days = max(0, (end_date - loan.due_on).days)
        amount_cents = 0 if late_days <= 2 else min(1000, late_days * 25)
        return FeeQuote(loan, late_days, amount_cents)


class PaymentApplication:
    def __init__(self, repository: LoanRepository, gateway: PaymentGateway):
        self.repository = repository
        self.gateway = gateway

    def pay(self, loan_id: str) -> PaymentResult:
        if self.repository.find(loan_id) is None:
            return PaymentResult(404, b'no such loan\n')

        try:
            response = self.gateway.charge(loan_id)
        except InterruptedError as interruption:
            return PaymentResult(502, b'payment gateway unavailable\n', interruption)
        except OSError:
            return PaymentResult(502, b'payment gateway unavailable\n')

        return PaymentResult(200 if response.status == 200 else 502, response.body)
