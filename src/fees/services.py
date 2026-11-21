from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol


class FeeLoanRecord(Protocol):
    id: str
    due_on: date
    returned_on: date | None


class FeeRepository(Protocol):
    def find(self, loan_id: str) -> FeeLoanRecord | None: ...


class Clock(Protocol):
    def today(self) -> date: ...


@dataclass
class LateFee:
    loan_id: str
    due_on: date
    late_days: int
    amount: Decimal


class FeeApplication:
    def __init__(self, repository: FeeRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def calculate(self, loan_id: str) -> LateFee | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        reference_date = loan.returned_on or self.clock.today()
        late_days = max(0, (reference_date - loan.due_on).days)
        amount = (
            Decimal('0.00')
            if late_days <= 2
            else min(
                Decimal(late_days) * Decimal('0.25'),
                Decimal('10.00'),
            )
        )
        return LateFee(
            loan_id=loan.id,
            due_on=loan.due_on,
            late_days=late_days,
            amount=amount,
        )


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> tuple[int, str]: ...


class PaymentApplication:
    def __init__(self, repository: FeeRepository, gateway: PaymentGateway):
        self.repository = repository
        self.gateway = gateway

    def pay(self, loan_id: str) -> tuple[str, int, str]:
        if self.repository.find(loan_id) is None:
            return 'missing', 404, 'no such loan\n'

        try:
            gateway_status, body = self.gateway_charge(loan_id)
        except (InterruptedError, OSError):
            return 'failure', 502, 'payment gateway unavailable\n'

        if gateway_status == 200:
            return 'success', 200, body
        return 'failure', 502, body

    def gateway_charge(self, loan_id: str) -> tuple[int, str]:
        return self.gateway.charge(loan_id)
