from dataclasses import dataclass

from src.loans.services import Clock, LoanRecord, LoanRepository


@dataclass(frozen=True)
class FeeQuote:
    loan: LoanRecord
    days_late: int
    amount_cents: int

    @property
    def formatted_amount(self) -> str:
        return f'${self.amount_cents // 100}.{self.amount_cents % 100:02d}'


class FeeApplication:
    def __init__(self, repository: LoanRepository, clock: Clock):
        self.repository = repository
        self.clock = clock

    def quote(self, loan_id: str) -> FeeQuote | None:
        loan = self.repository.find(loan_id)
        if loan is None:
            return None

        end_date = loan.returned_on or self.clock.today()
        days_late = max(0, (end_date - loan.due_on).days)
        amount_cents = 0 if days_late <= 2 else min(days_late * 25, 1000)
        return FeeQuote(loan, days_late, amount_cents)


class PaymentApplication:
    def __init__(self, repository: LoanRepository, gateway):
        self.repository = repository
        self.gateway = gateway

    def pay(self, loan_id: str):
        if self.repository.find(loan_id) is None:
            return None
        return self.gateway.charge(loan_id)
