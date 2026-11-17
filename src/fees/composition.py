from src.loans.repository import DjangoLoanRepository

from .clock import ServerLocalClock
from .gateway import HttpPaymentGateway
from .payments import PaymentApplication
from .services import FeeApplication

loan_repository = DjangoLoanRepository()
fee_application = FeeApplication(loan_repository, ServerLocalClock())
payment_application = PaymentApplication(loan_repository, HttpPaymentGateway())
