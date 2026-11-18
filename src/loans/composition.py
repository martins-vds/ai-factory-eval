from .clock import SystemClock
from .repository import LoanRepository
from .services import LoanUseCases


def loan_use_cases():
    return LoanUseCases(LoanRepository(), SystemClock())
