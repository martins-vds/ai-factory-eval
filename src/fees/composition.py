from src.loans.clock import SystemClock
from src.loans.repository import DjangoLoanRepository

from .gateway import HttpPaymentGateway
from .services import FeeApplication, PaymentApplication

loan_repository = DjangoLoanRepository()
fee_application = FeeApplication(loan_repository, SystemClock())
payment_application = PaymentApplication(loan_repository, HttpPaymentGateway())
