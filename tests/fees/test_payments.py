import pytest

from src.fees.services import LoanNotFound, PaymentApplication


class LoanRepository:
    def find(self, loan_id):
        return None


class PaymentGateway:
    def __init__(self):
        self.charges = []

    def charge(self, loan_id):
        self.charges.append(loan_id)


class ExistingLoanRepository:
    def find(self, loan_id):
        return object()


class InterruptedPaymentGateway:
    def charge(self, loan_id):
        raise InterruptedError('request interrupted')


def test_payment_rejects_an_unknown_loan_before_calling_the_gateway():
    gateway = PaymentGateway()
    application = PaymentApplication(LoanRepository(), gateway)

    with pytest.raises(LoanNotFound):
        application.pay('L9')

    assert gateway.charges == []


def test_payment_application_does_not_swallow_an_interruption():
    application = PaymentApplication(ExistingLoanRepository(), InterruptedPaymentGateway())

    with pytest.raises(InterruptedError):
        application.pay('L1')
