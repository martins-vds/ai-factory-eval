from src.loans.repository import DjangoLoanRepository

from .clock import ServerLocalClock
from .gateway import HttpPaymentGateway
from .services import FeeApplication, PaymentApplication

loan_repository = DjangoLoanRepository()
fee_application = FeeApplication(loan_repository, ServerLocalClock())
payment_application = PaymentApplication(loan_repository, HttpPaymentGateway())
