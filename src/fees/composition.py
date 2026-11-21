from src.loans.repository import DjangoLoanRepository

from .clock import SystemClock
from .gateway import HttpPaymentGateway
from .repository import DjangoFeeRepository
from .services import FeeApplication, PaymentApplication

fee_application = FeeApplication(DjangoFeeRepository(), SystemClock())
payment_application = PaymentApplication(DjangoLoanRepository(), HttpPaymentGateway())
