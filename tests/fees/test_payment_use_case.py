from dataclasses import dataclass
from datetime import date

from src.fees.services import FeeApplication, GatewayResponse


@dataclass
class Loan:
    id: str
    due_on: date
    returned_on: date | None = None


class InMemoryLoanRepository:
    def __init__(self, *loans):
        self.loans = {loan.id: loan for loan in loans}

    def find(self, loan_id):
        return self.loans.get(loan_id)


class FixedClock:
    def today(self):
        return date(2026, 11, 9)


class RecordingGateway:
    def __init__(self):
        self.charges = []

    def charge(self, loan_id):
        self.charges.append(loan_id)
        return GatewayResponse(200, 'charged\n')


def test_payment_use_case_charges_existing_loan_through_injected_ports():
    repository = InMemoryLoanRepository(Loan('L1', date(2026, 11, 1)))
    gateway = RecordingGateway()
    application = FeeApplication(repository, FixedClock(), gateway)

    result = application.pay('L1')

    assert result == GatewayResponse(200, 'charged\n')
    assert gateway.charges == ['L1']


def test_payment_use_case_does_not_charge_unknown_loan():
    gateway = RecordingGateway()
    application = FeeApplication(InMemoryLoanRepository(), FixedClock(), gateway)

    result = application.pay('missing')

    assert result is None
    assert gateway.charges == []
