from src.loans.repository import DjangoLoanRepository
from src.loans.services import LoanCatalog


def loan_catalog() -> LoanCatalog:
    return LoanCatalog(DjangoLoanRepository())
