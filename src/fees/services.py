from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    due_on: date
    returned_on: date | None


class LoanRepository(Protocol):
    def all(self) -> list[LoanRecord]: ...

    def find(self, loan_id: str) -> LoanRecord | None: ...


class Clock(Protocol):
    def today(self) -> date: ...


@dataclass(frozen=True)
class GatewayResponse:
    status: int
    body: str


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


@dataclass(frozen=True)
class FeeQuote:
    loan: LoanRecord
    days_late: int
    amount: Decimal


@dataclass(frozen=True)
class PaymentResult:
    status: int
    body: str
    interruption: InterruptedError | None = None


class FeeApplication:
    def __init__(self, loans: LoanRepository, clock: Clock, gateway: PaymentGateway):
        self.loans = loans
        self.clock = clock
        self.gateway = gateway

    def fee_for(self, loan_id: str) -> FeeQuote | None:
        loan = self.loans.find(loan_id)
        if loan is None:
            return None
        return self._quote(loan)

    def fees(self) -> list[FeeQuote]:
        return [self._quote(loan) for loan in self.loans.all()]

    def pay(self, loan_id: str) -> PaymentResult:
        if self.loans.find(loan_id) is None:
            return PaymentResult(404, 'no such loan\n')

        try:
            response = self.gateway.charge(loan_id)
        except InterruptedError as interruption:
            return PaymentResult(502, 'payment gateway unavailable\n', interruption)
        except OSError:
            return PaymentResult(502, 'payment gateway unavailable\n')

        return PaymentResult(
            response.status if response.status == 200 else 502,
            response.body,
        )

    def _quote(self, loan: LoanRecord) -> FeeQuote:
        end = loan.returned_on or self.clock.today()
        days_late = max(0, (end - loan.due_on).days)
        cents = 0 if days_late <= 2 else min(1000, days_late * 25)
        return FeeQuote(loan, days_late, Decimal(cents) / 100)
