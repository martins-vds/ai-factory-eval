from src.loans.clock import SystemClock
from src.loans.repository import DjangoLoanRepository

from .gateway import HttpPaymentGateway
from .services import LateFeeApplication, PaymentApplication

loan_repository = DjangoLoanRepository()
clock = SystemClock()
late_fee_application = LateFeeApplication(loan_repository, clock)
payment_application = PaymentApplication(loan_repository, HttpPaymentGateway())
