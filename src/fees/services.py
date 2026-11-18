from dataclasses import dataclass
from datetime import date
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
class FeeQuote:
    loan: LoanRecord
    late_days: int
    amount_cents: int

    @property
    def amount(self):
        return f'${self.amount_cents // 100}.{self.amount_cents % 100:02d}'


class FeeApplication:
    def __init__(self, loans: LoanRepository, clock: Clock):
        self.loans = loans
        self.clock = clock

    def calculate(self, loan_id: str) -> FeeQuote | None:
        loan = self.loans.find(loan_id)
        return self.calculate_for(loan) if loan else None

    def all_fees(self) -> list[FeeQuote]:
        return [self.calculate_for(loan) for loan in self.loans.all()]

    def calculate_for(self, loan: LoanRecord) -> FeeQuote:
        end_date = loan.returned_on or self.clock.today()
        late_days = max(0, (end_date - loan.due_on).days)
        amount_cents = 0 if late_days <= 2 else min(1000, late_days * 25)
        return FeeQuote(loan, late_days, amount_cents)


@dataclass(frozen=True)
class GatewayResponse:
    status_code: int
    body: str


class PaymentGatewayError(Exception):
    pass


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


@dataclass(frozen=True)
class PaymentResult:
    status_code: int
    body: str
    failure: PaymentGatewayError | None = None
    loan: LoanRecord | None = None

    @property
    def succeeded(self):
        return self.status_code == 200


class PaymentApplication:
    def __init__(self, loans: LoanRepository, gateway: PaymentGateway):
        self.loans = loans
        self.gateway = gateway

    def pay(self, loan_id: str) -> PaymentResult:
        loan = self.loans.find(loan_id)
        if loan is None:
            return PaymentResult(404, 'no such loan\n')

        try:
            response = self.gateway.charge(loan_id)
        except PaymentGatewayError as exc:
            return PaymentResult(502, 'payment gateway unavailable\n', exc, loan)

        return PaymentResult(
            200 if response.status_code == 200 else 502,
            response.body,
            loan=loan,
        )
