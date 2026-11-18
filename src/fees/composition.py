from src.loans.clock import SystemClock
from src.loans.repository import DjangoLoanRepository

from .services import FeeApplication

fee_application = FeeApplication(DjangoLoanRepository(), SystemClock())
