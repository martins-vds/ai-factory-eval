from datetime import date
from typing import NamedTuple, Protocol


class LoanRecord(Protocol):
    id: str
    due_on: date
    returned_on: date | None


class Clock(Protocol):
    def today(self) -> date: ...


class LoanRepository(Protocol):
    def find(self, loan_id: str) -> LoanRecord | None: ...


class GatewayResponse(NamedTuple):
    status: int
    body: str


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


class PaymentGatewayFailure(Exception):
    pass


class InterruptedPayment(PaymentGatewayFailure):
    pass


class FeeQuote(NamedTuple):
    loan: LoanRecord
    days_late: int
    amount_cents: int


class FeeApplication:
    def __init__(
        self,
        repository: LoanRepository,
        clock: Clock,
        gateway: PaymentGateway,
    ):
        self.repository = repository
        self.clock = clock
        self.gateway = gateway

    def calculate_fee(self, loan_id: str) -> FeeQuote | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        days_late = max(0, (end_date - loan.due_on).days)
        amount_cents = 0 if days_late <= 2 else min(1000, days_late * 25)
        return FeeQuote(loan, days_late, amount_cents)

    def pay(self, loan_id: str) -> GatewayResponse | None:
        if self.repository.find(loan_id) is None:
            return None
        response = self.gateway.charge(loan_id)
        return GatewayResponse(200 if response.status == 200 else 502, response.body)
