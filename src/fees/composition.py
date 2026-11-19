from src.loans.clock import SystemClock
from src.loans.repository import DjangoLoanRepository

from .gateway import HttpPaymentGateway
from .services import LateFeeApplication, PaymentApplication

fee_application = LateFeeApplication(DjangoLoanRepository(), SystemClock())
payment_application = PaymentApplication(DjangoLoanRepository(), HttpPaymentGateway())
