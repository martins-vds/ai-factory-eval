from .repository import LoanRepository
from .services import get_loan_text as get_loan, list_loans_text as list_loans, loan_line


def list_loans_text():
    return list_loans(LoanRepository())


def get_loan_text(loan_id):
    return get_loan(LoanRepository(), loan_id)
