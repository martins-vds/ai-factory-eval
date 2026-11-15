from dataclasses import dataclass
from datetime import date
from typing import Protocol


class LoanRecord(Protocol):
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


class PaymentGatewayError(Exception):
    pass


class PaymentGatewayInterrupted(PaymentGatewayError):
    pass


class PaymentGatewayUnavailable(PaymentGatewayError):
    pass


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


@dataclass(frozen=True)
class LateFeeQuote:
    loan: LoanRecord
    days_late: int
    amount_cents: int

    @property
    def formatted_amount(self) -> str:
        return f'${self.amount_cents // 100}.{self.amount_cents % 100:02d}'


class FeeApplication:
    def __init__(self, loan_repository: LoanRepository, clock: Clock):
        self.loan_repository = loan_repository
        self.clock = clock

    def quote_for(self, loan_id: str) -> LateFeeQuote | None:
        loan = self.loan_repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        days_late = max(0, (end_date - loan.due_on).days)
        amount_cents = 0 if days_late <= 2 else min(days_late * 25, 1000)
        return LateFeeQuote(loan, days_late, amount_cents)


class PaymentApplication:
    def __init__(self, loan_repository: LoanRepository, gateway: PaymentGateway):
        self.loan_repository = loan_repository
        self.gateway = gateway

    def pay(self, loan_id: str) -> GatewayResponse | None:
        if self.loan_repository.find(loan_id) is None:
            return None
        return self.gateway.charge(loan_id)
