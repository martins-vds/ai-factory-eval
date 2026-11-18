from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from http.client import HTTPException
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
class LateFee:
    loan: Loan
    days_late: int
    amount: Decimal


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


class PaymentInterrupted(Exception):
    pass


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def for_loan(self, loan_id: str) -> LateFee | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        days_late = max(0, (end_date - loan.due_on).days)
        amount_cents = min(days_late * 25 if days_late > 2 else 0, 1000)
        return LateFee(loan, days_late, Decimal(amount_cents) / 100)


class PaymentApplication:
    def __init__(self, repository: LoanRepository, gateway: PaymentGateway):
        self.repository = repository
        self.gateway = gateway

    def pay(self, loan_id: str) -> PaymentResult | None:
        if self.repository.find(loan_id) is None:
            return None

        try:
            response = self.gateway.charge(loan_id)
        except InterruptedError as error:
            raise PaymentInterrupted from error
        except (OSError, HTTPException):
            return PaymentResult(502, b'payment gateway unavailable\n')

        return PaymentResult(200 if response.status == 200 else 502, response.body)
