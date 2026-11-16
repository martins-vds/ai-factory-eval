from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class FeeLoan:
    id: str
    due_on: date
    returned_on: date | None


@dataclass(frozen=True)
class FeeQuote:
    loan_id: str
    due_on: date
    days_late: int
    amount: Decimal


@dataclass(frozen=True)
class GatewayResponse:
    status_code: int
    body: bytes


@dataclass(frozen=True)
class PaymentResult:
    status_code: int
    body: bytes
    failure: Exception | None = None


class PaymentGatewayUnavailable(Exception):
    pass


class PaymentGatewayInterrupted(PaymentGatewayUnavailable):
    pass


class Clock(Protocol):
    def today(self) -> date: ...


class LoanRepository(Protocol):
    def find(self, loan_id: str) -> FeeLoan | None: ...


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


class LateFeeApplication:
    def __init__(
        self,
        loans: LoanRepository,
        clock: Clock,
        payment_gateway: PaymentGateway,
    ):
        self.loans = loans
        self.clock = clock
        self.payment_gateway = payment_gateway

    def fee(self, loan_id: str) -> FeeQuote | None:
        loan = self.loans.find(loan_id)
        if loan is None:
            return None

        assessed_on = loan.returned_on or self.clock.today()
        days_late = max(0, (assessed_on - loan.due_on).days)
        amount = Decimal('0.00')
        if days_late > 2:
            amount = min(Decimal(days_late) * Decimal('0.25'), Decimal('10.00'))
        return FeeQuote(loan.id, loan.due_on, days_late, amount)

    def pay(self, loan_id: str) -> PaymentResult | None:
        if self.loans.find(loan_id) is None:
            return None

        try:
            response = self.payment_gateway.charge(loan_id)
        except PaymentGatewayInterrupted as failure:
            return PaymentResult(
                502,
                b'payment gateway unavailable\n',
                failure,
            )
        except PaymentGatewayUnavailable as failure:
            return PaymentResult(
                502,
                b'payment gateway unavailable\n',
                failure,
            )
        status_code = 200 if response.status_code == 200 else 502
        return PaymentResult(status_code, response.body)
