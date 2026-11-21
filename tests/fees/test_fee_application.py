from dataclasses import dataclass
from datetime import date

from src.fees.services import FeeApplication, GatewayResponse


@dataclass
class Loan:
    id: str
    due_on: date
    returned_on: date | None = None


class InMemoryLoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan and self.loan.id == loan_id else None


class Clock:
    def today(self):
        return date(2026, 1, 1)


class PaymentGateway:
    def __init__(self):
        self.loan_ids = []
        self.response = GatewayResponse(200, 'charged\n')

    def charge(self, loan_id):
        self.loan_ids.append(loan_id)
        return self.response


def test_pay_requires_an_existing_loan_without_calling_the_gateway():
    gateway = PaymentGateway()
    application = FeeApplication(InMemoryLoanRepository(None), Clock(), gateway)

    result = application.pay('missing')

    assert result is None
    assert gateway.loan_ids == []


def test_pay_uses_the_injected_gateway_for_an_existing_loan():
    gateway = PaymentGateway()
    loan = Loan('L1', date(2026, 1, 1))
    application = FeeApplication(InMemoryLoanRepository(loan), Clock(), gateway)

    result = application.pay('L1')

    assert result == gateway.response
    assert gateway.loan_ids == ['L1']
