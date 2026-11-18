from .clock import SystemClock
from .repository import LoanRepository
from .services import (
    get_loan_text as get_loan_text_use_case,
    lend_loan,
    list_loans_text as list_loans_text_use_case,
    return_loan,
)


def all_loans():
    return LoanRepository().all()


def find_loan(loan_id):
    return LoanRepository().find(loan_id)


def list_loans_text():
    return list_loans_text_use_case(LoanRepository())


def get_loan_text(loan_id):
    return get_loan_text_use_case(LoanRepository(), loan_id)


def lend(member, isbn):
    return lend_loan(LoanRepository(), SystemClock(), member, isbn)


def give_back(loan_id):
    return return_loan(LoanRepository(), SystemClock(), loan_id)
