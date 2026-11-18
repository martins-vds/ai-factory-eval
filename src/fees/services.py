from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol


class LoanRecord(Protocol):
    id: str
    member: str
    due_on: date
    returned_on: date | None


class Clock(Protocol):
    def today(self) -> date: ...


class LoanRepository(Protocol):
    def all(self) -> Iterable[LoanRecord]: ...

    def find(self, loan_id: str) -> LoanRecord | None: ...


@dataclass(frozen=True)
class PaymentResult:
    status: int
    body: str


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> PaymentResult: ...


@dataclass(frozen=True)
class Fee:
    loan: LoanRecord
    days_late: int
    amount: Decimal


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock, gateway: PaymentGateway):
        self.repository = repository
        self.clock = clock
        self.gateway = gateway

    def calculate(self, loan_id: str) -> Fee | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        return self._calculate(loan, self.clock.today())

    def all_fees(self) -> list[Fee]:
        today = self.clock.today()
        return [self._calculate(loan, today) for loan in self.repository.all()]

    def pay(self, loan_id: str) -> PaymentResult | None:
        if self.repository.find(loan_id) is None:
            return None
        return self.gateway.charge(loan_id)

    @staticmethod
    def _calculate(loan: LoanRecord, today: date) -> Fee:
        end_date = loan.returned_on or today
        days_late = max(0, (end_date - loan.due_on).days)
        cents = 0 if days_late <= 2 else min(days_late * 25, 1000)
        amount = (Decimal(cents) / Decimal(100)).quantize(Decimal('0.00'))
        return Fee(loan, days_late, amount)
