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


@dataclass(frozen=True)
class GatewayResponse:
    status_code: int
    body: str


class PaymentGateway(Protocol):
    def charge(self, loan_id: str) -> GatewayResponse: ...


@dataclass(frozen=True)
class FeeQuote:
    loan: LoanRecord
    late_days: int
    amount_cents: int


@dataclass(frozen=True)
class PaymentResult:
    status_code: int
    body: str
    interruption: InterruptedError | None = None


class GatewayUnavailable(Exception):
    def __init__(self, interruption: InterruptedError | None = None):
        super().__init__('payment gateway unavailable')
        self.interruption = interruption


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def calculate_fee(self, loan_id: str) -> FeeQuote | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        late_days = max(0, (end_date - loan.due_on).days)
        amount_cents = 0 if late_days <= 2 else min(1000, late_days * 25)
        return FeeQuote(loan, late_days, amount_cents)


class PaymentApplication:
    def __init__(self, repository: LoanRepository, gateway: PaymentGateway):
        self.repository = repository
        self.gateway = gateway

    def pay(self, loan_id: str) -> PaymentResult | None:
        if self.repository.find(loan_id) is None:
            return None

        try:
            response = self.gateway.charge(loan_id)
        except InterruptedError as exc:
            return PaymentResult(502, 'payment gateway unavailable\n', exc)
        except GatewayUnavailable as exc:
            return PaymentResult(502, 'payment gateway unavailable\n', exc.interruption)
        except OSError:
            return PaymentResult(502, 'payment gateway unavailable\n')

        status_code = 200 if response.status_code == 200 else 502
        return PaymentResult(status_code, response.body)
