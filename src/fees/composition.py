from src.loans.clock import SystemClock
from src.loans.repository import DjangoLoanRepository

from .services import FeesApplication

fees_application = FeesApplication(DjangoLoanRepository(), SystemClock())
