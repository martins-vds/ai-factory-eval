from .clock import SystemClock
from .repository import LoanRepository
from .services import LendBook, ReturnBook


def lend_loan(member, isbn):
    return LendBook(LoanRepository(), SystemClock()).execute(member, isbn)


def return_loan(loan_id):
    return ReturnBook(LoanRepository(), SystemClock()).execute(loan_id)
