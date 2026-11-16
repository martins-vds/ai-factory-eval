from dataclasses import dataclass
from datetime import date

from src.fees.services import FeeApplication, GatewayResponse


@dataclass
class Loan:
    id: str


class InMemoryLoanRepository:
    def __init__(self, *loans):
        self.loans = {loan.id: loan for loan in loans}

    def find(self, loan_id):
        return self.loans.get(loan_id)


class FixedClock:
    def today(self):
        return date(2026, 11, 9)


class InMemoryPaymentGateway:
    def __init__(self):
        self.charges = []

    def charge(self, loan_id):
        self.charges.append(loan_id)
        return GatewayResponse(200, 'charged\n')


def test_pay_uses_injected_loan_repository_and_gateway():
    repository = InMemoryLoanRepository(Loan('L1'))
    gateway = InMemoryPaymentGateway()
    application = FeeApplication(repository, FixedClock(), gateway)

    response = application.pay('L1')

    assert response == GatewayResponse(200, 'charged\n')
    assert gateway.charges == ['L1']


def test_pay_does_not_charge_unknown_loan():
    gateway = InMemoryPaymentGateway()
    application = FeeApplication(InMemoryLoanRepository(), FixedClock(), gateway)

    response = application.pay('missing')

    assert response is None
    assert gateway.charges == []
