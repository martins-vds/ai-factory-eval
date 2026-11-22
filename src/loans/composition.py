from .clock import SystemClock
from .repository import LoanRepository


def loan_repository():
    return LoanRepository()


def system_clock():
    return SystemClock()
