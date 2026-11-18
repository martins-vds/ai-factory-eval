from src.loans.clock import SystemClock
from src.loans.repository import DjangoLoanRepository

from .gateway import HttpPaymentGateway
from .services import FeeApplication, PaymentApplication

fee_application = FeeApplication(DjangoLoanRepository(), SystemClock())
payment_application = PaymentApplication(DjangoLoanRepository(), HttpPaymentGateway())
