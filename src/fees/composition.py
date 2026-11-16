from src.loans.clock import SystemClock

from .gateway import HttpPaymentGateway
from .repository import DjangoFeeRepository
from .services import FeeApplication

fee_application = FeeApplication(
    DjangoFeeRepository(),
    SystemClock(),
    HttpPaymentGateway(),
)
