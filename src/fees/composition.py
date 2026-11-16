from src.loans.clock import SystemClock

from .gateway import HttpPaymentGateway
from .repository import DjangoFeeLoanRepository
from .services import LateFeeApplication

fee_application = LateFeeApplication(
    DjangoFeeLoanRepository(),
    SystemClock(),
    HttpPaymentGateway(),
)
