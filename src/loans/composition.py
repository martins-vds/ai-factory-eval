from .repository import LoanRepository
from .services import LoanService


def get_loan_service():
    return LoanService(LoanRepository())
