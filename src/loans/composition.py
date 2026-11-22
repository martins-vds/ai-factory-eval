from .clock import DjangoClock
from .repository import LoanRepository
from .services import LoanApplication


def loan_application():
    return LoanApplication(LoanRepository(), DjangoClock())
