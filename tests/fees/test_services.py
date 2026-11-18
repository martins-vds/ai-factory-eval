from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from src.fees.services import FeeApplication


@dataclass
class Loan:
    id: str
    due_on: date
    member: str = 'reader'
    returned_on: date | None = None


class LoanRepository:
    def __init__(self, loan):
        self.loan = loan

    def find(self, loan_id):
        return self.loan if loan_id == self.loan.id else None


class Clock:
    def today(self):
        return date(2026, 11, 18)


class PaymentGateway:
    def charge(self, loan_id):
        raise AssertionError('fee calculation must not charge a payment')


def test_late_fee_waives_the_first_two_days_and_charges_the_third():
    loan = Loan(id='L1', due_on=date(2026, 11, 16))
    application = FeeApplication(LoanRepository(loan), Clock(), PaymentGateway())

    two_days_late = application.calculate(loan.id)
    loan.due_on = date(2026, 11, 15)
    three_days_late = application.calculate(loan.id)

    assert (two_days_late.days_late, two_days_late.amount) == (2, Decimal('0.00'))
    assert (three_days_late.days_late, three_days_late.amount) == (3, Decimal('0.75'))


def test_late_fee_uses_return_date_and_never_exceeds_ten_dollars():
    loan = Loan(
        id='L1',
        due_on=date(2026, 1, 1),
        returned_on=date(2026, 3, 1),
    )
    application = FeeApplication(LoanRepository(loan), Clock(), PaymentGateway())

    fee = application.calculate(loan.id)

    assert fee.days_late == 59
    assert fee.amount == Decimal('10.00')
