from src.loans.clock import SystemClock
from src.loans.repository import DjangoLoanRepository

from .gateway import HttpPaymentGateway
from .payments import PaymentApplication
from .services import FeeApplication

loan_repository = DjangoLoanRepository()
fee_application = FeeApplication(loan_repository, SystemClock())
payment_application = PaymentApplication(loan_repository, HttpPaymentGateway())
