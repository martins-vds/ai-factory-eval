from src.loans.clock import SystemClock
from src.loans.repository import DjangoLoanRepository

from .gateway import PaymentGateway
from .services import FeesApplication

fees_application = FeesApplication(DjangoLoanRepository(), SystemClock())
payment_gateway = PaymentGateway()
