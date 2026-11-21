from src.loans.clock import SystemClock

from .gateway import HttpPaymentGateway
from .repository import DjangoLoanRepository
from .services import FeeApplication

fee_application = FeeApplication(
    DjangoLoanRepository(),
    SystemClock(),
    HttpPaymentGateway(),
)
