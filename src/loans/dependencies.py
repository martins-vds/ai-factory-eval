from .repositories import DjangoLoanRepository
from .services import LoanCatalog

loan_catalog = LoanCatalog(DjangoLoanRepository())
