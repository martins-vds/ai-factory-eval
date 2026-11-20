from dataclasses import dataclass
from datetime import date
from decimal import Decimal
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
class GatewayResponse:
    status_code: int
    body: str


@dataclass(frozen=True)
class PaymentResult:
    status_code: int
    body: str
    interruption: InterruptedError | None = None


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


@dataclass(frozen=True)
class LateFee:
    loan: LoanRecord
    late_days: int
    amount: Decimal


class FeeApplication:
    def __init__(self, loan_repository: LoanRepository, clock: Clock):
        self.loan_repository = loan_repository
        self.clock = clock

    def fee_for(self, loan_id: str) -> LateFee | None:
        loan = self.loan_repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        late_days = max(0, (end_date - loan.due_on).days)
        cents = 0 if late_days <= 2 else min(1000, late_days * 25)
        return LateFee(loan, late_days, Decimal(cents) / 100)


class PaymentApplication:
    def __init__(self, loan_repository: LoanRepository, gateway: PaymentGateway):
        self.loan_repository = loan_repository
        self.gateway = gateway

    def pay(self, loan_id: str) -> PaymentResult | None:
        if self.loan_repository.find(loan_id) is None:
            return None

        try:
            response = self.gateway.charge(loan_id)
        except InterruptedError as interruption:
            return PaymentResult(502, 'payment gateway unavailable\n', interruption)
        except OSError:
            return PaymentResult(502, 'payment gateway unavailable\n')

        status_code = 200 if response.status_code == 200 else 502
        return PaymentResult(status_code, response.body)
