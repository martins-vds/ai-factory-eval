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


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> 'GatewayResponse': ...


@dataclass(frozen=True)
class GatewayResponse:
    status_code: int
    body: str


@dataclass(frozen=True)
class FeeQuote:
    loan: LoanRecord
    late_days: int
    amount_cents: int

    @property
    def amount(self):
        return f'${self.amount_cents // 100}.{self.amount_cents % 100:02d}'


class PaymentGatewayFailure(Exception):
    pass


@dataclass(frozen=True)
class PaymentOutcome:
    status_code: int
    body: str
    failure: PaymentGatewayFailure | None = None


class FeeApplication:
    def __init__(self, loans: LoanRepository, clock: Clock, gateway: PaymentGateway):
        self.loans = loans
        self.clock = clock
        self.gateway = gateway

    def quote(self, loan_id: str) -> FeeQuote | None:
        loan = self.loans.find(loan_id)
        if loan is None:
            return None

        effective_date = loan.returned_on or self.clock.today()
        late_days = max(0, (effective_date - loan.due_on).days)
        amount_cents = 0 if late_days <= 2 else min(late_days * 25, 1000)
        return FeeQuote(loan, late_days, amount_cents)

    def pay(self, loan_id: str) -> PaymentOutcome | None:
        if self.loans.find(loan_id) is None:
            return None

        try:
            gateway_response = self.gateway.charge(loan_id)
        except PaymentGatewayFailure as failure:
            return PaymentOutcome(
                502,
                'payment gateway unavailable\n',
                failure,
            )
        status_code = 200 if gateway_response.status_code == 200 else 502
        return PaymentOutcome(status_code, gateway_response.body)
