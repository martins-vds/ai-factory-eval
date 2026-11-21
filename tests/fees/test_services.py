from dataclasses import dataclass
from datetime import date

from src.fees.services import FeeApplication, GatewayResponse


@dataclass
class Loan:
    id: str
    due_on: date
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if self.loan and self.loan.id == loan_id else None


class Clock:
    def today(self):
        return date(2026, 1, 1)


class PaymentGateway:
    def __init__(self, response):
        self.response = response
        self.charges = []

    def charge(self, loan_id):
        self.charges.append(loan_id)
        return self.response


def test_pay_refuses_unknown_loan_without_calling_gateway():
    gateway = PaymentGateway(GatewayResponse(200, 'charged\n'))
    application = FeeApplication(LoanRepository(None), Clock(), gateway)

    assert application.pay('missing') is None
    assert gateway.charges == []


def test_pay_calls_gateway_for_existing_loan_and_returns_response():
    response = GatewayResponse(200, 'charged\n')
    gateway = PaymentGateway(response)
    application = FeeApplication(LoanRepository(Loan('L1', date(2026, 1, 1))), Clock(), gateway)

    assert application.pay('L1') is response
    assert gateway.charges == ['L1']
